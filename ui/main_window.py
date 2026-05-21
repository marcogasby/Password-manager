import secrets
import string
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLineEdit, QLabel, 
                             QPushButton, QTextEdit, QComboBox, QInputDialog, 
                             QMessageBox, QSlider, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QGuiApplication

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, db_manager, current_user="Utente"):
        super().__init__()
        self.db = db_manager
        self.current_user = current_user
        self.selected_item_id = None
        
        # Timer per svuotare gli appunti
        self.clipboard_timer = QTimer()
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.timeout.connect(self.clear_clipboard)
        
        self.init_ui()
        self.load_categories()
        self.load_items()
        self.open_personal_dashboard() # Mostra la dashboard personale a tutto schermo all'avvio

    def init_ui(self):
        self.setWindowTitle("Fortress - Password Manager")
        self.resize(1150, 680)
        
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #0d1117; 
            }
            QWidget {
                color: #c9d1d9; 
                font-family: 'Segoe UI', -apple-system, sans-serif; 
            }
            QWidget#SidebarWidget {
                background-color: #16191e;
                border-right: 1px solid #2d3545;
            }
            QLabel {
                background-color: transparent;
                font-weight: 600;
                color: #9ca3af;
                font-size: 13px;
            }
            QListWidget { 
                background-color: #1f242d; 
                border: 1px solid #2d3545; 
                border-radius: 8px;
                padding: 8px; 
            }
            QListWidget::item { 
                padding: 12px; 
                border-radius: 6px; 
                margin-bottom: 4px;
                color: #e3e6eb;
            }
            QListWidget::item:hover {
                background-color: #2d3545;
            }
            QListWidget::item:selected { 
                background-color: #1f6feb; 
                color: white; 
            }
            QLineEdit, QTextEdit, QComboBox { 
                background-color: #1f242d; 
                border: 1px solid #2d3545; 
                border-radius: 8px; 
                padding: 10px; 
                color: #ffffff; 
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #1f6feb;
            }
            QPushButton { 
                background-color: #1f242d; 
                border: 1px solid #2d3545; 
                border-radius: 8px; 
                padding: 10px 18px; 
                color: #e3e6eb; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #2d3545; 
            }
            QPushButton#AccentBtn { 
                background-color: #238636; 
                border: 1px solid #2ea043; 
                color: white; 
            }
            QPushButton#AccentBtn:hover { 
                background-color: #2ea043; 
            }
            QPushButton#DangerBtn { 
                background-color: #da3637; 
                color: white; 
                border: none; 
            }
            QPushButton#DangerBtn:hover { 
                background-color: #f85149; 
            }
            QPushButton#HomeBtn {
                border: none;
                background: transparent;
                font-size: 22px;
                color: #9ca3af;
                padding: 0px 5px;
            }
            QPushButton#HomeBtn:hover {
                color: #ffffff;
            }
        """)

        # Layout principale dell'applicazione (Orizzontale)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # -------------------------------------------------------------
        # COLONNA 1: SIDEBAR DI NAVIGAZIONE (Resta sempre fissa a sinistra)
        # -------------------------------------------------------------
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("SidebarWidget")
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(20, 20, 20, 20)
        sidebar.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        # 1) MODIFICA: Scritta Fortress colorata con il giallo ambra coordinato (#ffb703)
        title_label = QLabel("Fortress")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffb703;")
        
        self.home_btn = QPushButton("⌂")
        self.home_btn.setObjectName("HomeBtn")
        self.home_btn.setToolTip("Sconnetti e torna al Login")
        self.home_btn.clicked.connect(self.trigger_logout)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.home_btn, alignment=Qt.AlignmentFlag.AlignRight)
        sidebar.addLayout(header_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2d3545; max-height: 1px; border: none;")
        sidebar.addWidget(line)
        
        self.btn_toggle_personal = QPushButton("👤 Area Personale")
        self.btn_toggle_personal.setStyleSheet("text-align: left; padding-left: 12px; background-color: #1f242d;")
        self.btn_toggle_personal.clicked.connect(self.open_personal_dashboard)
        sidebar.addWidget(self.btn_toggle_personal)
        
        sidebar.addWidget(QLabel("CATEGORIE"))
        
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.filter_by_category)
        self.category_list.itemSelectionChanged.connect(self.toggle_category_delete_button)
        sidebar.addWidget(self.category_list)
        
        cat_buttons_layout = QHBoxLayout()
        add_cat_btn = QPushButton("+ Categoria")
        add_cat_btn.clicked.connect(self.add_category)
        cat_buttons_layout.addWidget(add_cat_btn, stretch=3)
        
        self.btn_delete_category = QPushButton("🗑️")
        self.btn_delete_category.setToolTip("Elimina la categoria selezionata")
        self.btn_delete_category.setEnabled(False)
        self.btn_delete_category.clicked.connect(self.delete_selected_category)
        cat_buttons_layout.addWidget(self.btn_delete_category, stretch=1)
        sidebar.addLayout(cat_buttons_layout)
        
        main_layout.addWidget(sidebar_widget, stretch=22)


        # -------------------------------------------------------------
        # BLOCCO DESTRO SWITCHABILE A SCHERMO INTERO (QStackedWidget)
        # -------------------------------------------------------------
        # Questo componente gestisce lo scambio totale delle restanti parti dello schermo
        self.content_stacked_widget = QStackedWidget()

        # --- PAGINA 1: INTERFACCIA STANDARD A DUE COLONNE (Lista Credenziali + Dettagli) ---
        standard_vault_page = QWidget()
        two_col_layout = QHBoxLayout(standard_vault_page)
        two_col_layout.setContentsMargins(0, 0, 0, 0)
        two_col_layout.setSpacing(0)

        # Sotto-Colonna A: Elenco Credenziali (Centro)
        center_widget = QWidget()
        center = QVBoxLayout(center_widget)
        center.setContentsMargins(20, 20, 20, 20)
        center.setSpacing(12)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Cerca credenziale...")
        self.search_bar.textChanged.connect(self.load_items)
        center.addWidget(self.search_bar)
        
        self.items_list = QListWidget()
        self.items_list.itemClicked.connect(self.display_item_details)
        center.addWidget(self.items_list)
        
        new_btn = QPushButton("+ Aggiungi Account")
        new_btn.setObjectName("AccentBtn")
        new_btn.clicked.connect(self.prepare_for_new_item)
        center.addWidget(new_btn)
        
        two_col_layout.addWidget(center_widget, stretch=45)

        # Sotto-Colonna B: Modulo Informazioni Dettagliate (Destra)
        details_widget = QWidget()
        details = QVBoxLayout(details_widget)
        details.setContentsMargins(20, 20, 20, 20)
        details.setSpacing(10)
        
        self.title_in = QLineEdit()
        self.user_in = QLineEdit()
        self.pass_in = QLineEdit()
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        self.url_in = QLineEdit()
        self.notes_in = QTextEdit()
        self.cat_combo = QComboBox()

        details.addWidget(QLabel("Servizio / Sito Web:"))
        details.addWidget(self.title_in)
        
        details.addWidget(QLabel("Username o Email:"))
        u_lay = QHBoxLayout()
        u_lay.addWidget(self.user_in)
        c_u = QPushButton("Copia")
        c_u.clicked.connect(lambda: self.copy_to_clipboard(self.user_in.text()))
        u_lay.addWidget(c_u)
        details.addLayout(u_lay)

        details.addWidget(QLabel("Password di sblocco:"))
        p_lay = QHBoxLayout()
        p_lay.addWidget(self.pass_in)
        t_p = QPushButton("👁️")
        t_p.setCheckable(True)
        t_p.clicked.connect(self.toggle_password)
        c_p = QPushButton("Copia")
        c_p.clicked.connect(lambda: self.copy_to_clipboard(self.pass_in.text(), True))
        p_lay.addWidget(t_p)
        p_lay.addWidget(c_p)
        details.addLayout(p_lay)

        self.slider_label = QLabel("📏 Lunghezza generatore: 16 caratteri")
        details.addWidget(self.slider_label)
        
        gen_lay = QHBoxLayout()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(8, 32)
        self.slider.setValue(16)
        self.slider.valueChanged.connect(self.update_slider_label)
        
        g_btn = QPushButton("Genera")
        g_btn.clicked.connect(self.generate_password)
        gen_lay.addWidget(self.slider)
        gen_lay.addWidget(g_btn)
        details.addLayout(gen_lay)

        details.addWidget(QLabel("URL Servizio:"))
        details.addWidget(self.url_in)
        details.addWidget(QLabel("Assegna Categoria:"))
        details.addWidget(self.cat_combo)
        details.addWidget(QLabel("Note personali:"))
        details.addWidget(self.notes_in)

        act_lay = QHBoxLayout()
        self.save_btn = QPushButton("Salva Modifiche")
        self.save_btn.setObjectName("AccentBtn")
        self.save_btn.clicked.connect(self.save_item)
        
        self.del_btn = QPushButton("🗑️ Elimina Account")
        self.del_btn.setObjectName("DangerBtn")
        self.del_btn.clicked.connect(self.delete_item)
        
        act_lay.addWidget(self.save_btn)
        act_lay.addWidget(self.del_btn)
        details.addLayout(act_lay)
        
        two_col_layout.addWidget(details_widget, stretch=55)
        
        self.content_stacked_widget.addWidget(standard_vault_page) # Indice 0


        # --- PAGINA 2: DASHBOARD AREA PERSONALE A TUTTO SCHERMO ---
        # 2) MODIFICA: Ora prende l'intero spazio centrale + destro quando attivata
        self.dashboard_page = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_page)
        dash_layout.setContentsMargins(40, 40, 40, 40)
        dash_layout.setSpacing(20)
        
        self.dash_title = QLabel("Pannello Utente")
        self.dash_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffb703; margin-bottom: 5px;")
        dash_layout.addWidget(self.dash_title)
        
        self.dash_stats = QLabel("Caricamento statistiche...")
        self.dash_stats.setStyleSheet("font-size: 15px; color: #e3e6eb;")
        dash_layout.addWidget(self.dash_stats)
        
        dash_layout.addSpacing(20)
        
        recent_headline = QLabel("⏱️ PASSWORD MODIFICATE DI RECENTE")
        recent_headline.setStyleSheet("font-size: 14px; font-weight: bold; color: #9ca3af;")
        dash_layout.addWidget(recent_headline)
        
        self.recent_items_list = QListWidget()
        self.recent_items_list.setStyleSheet("QListWidget { font-size: 14px; }")
        self.recent_items_list.setToolTip("Clicca su un elemento per aprirne i dettagli")
        self.recent_items_list.itemClicked.connect(self.open_recent_item)
        dash_layout.addWidget(self.recent_items_list)
        
        dash_layout.addStretch()
        
        self.content_stacked_widget.addWidget(self.dashboard_page) # Indice 1

        main_layout.addWidget(self.content_stacked_widget, stretch=78)

        # Rendering finale
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # --- AZIONI E LOGICHE DI TRANSIZIONE ---

    def open_personal_dashboard(self):
        """Attiva la Dashboard a tutto schermo (nascondendo la lista centrale e i dettagli)"""
        self.items_list.clearSelection()
        self.category_list.clearSelection() # Deseleziona la sidebar temporaneamente
        self.content_stacked_widget.setCurrentIndex(1) # Mostra Pagina Dashboard
        
        self.dash_title.setText(f"👤 Account: {self.current_user}")
        
        all_items = self.db.get_items()
        total_pwd = len(all_items)
        self.dash_stats.setText(f"Cassaforte cifrata localmente • Attualmente sono protetti <b>{total_pwd}</b> account salvati.")
        
        # Popola la lista delle password recenti (ultime 3 salvate/modificate)
        self.recent_items_list.clear()
        recent_items = all_items[-3:] if total_pwd >= 3 else all_items
        recent_items = list(reversed(recent_items))
        
        if not recent_items:
            li = QListWidgetItem("Nessun account salvato di recente in questa cassaforte.")
            li.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recent_items_list.addItem(li)
        else:
            for item in recent_items:
                li = QListWidgetItem(f"   🔑  {item['title']} ({item['username']})")
                li.setData(Qt.ItemDataRole.UserRole, item["id"])
                self.recent_items_list.addItem(li)

    def open_recent_item(self, item):
        """Cliccando un elemento recente, ripristina il layout a colonne e mostra il dettaglio"""
        item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_id is not None:
            # Ripristina la visualizzazione standard
            self.content_stacked_widget.setCurrentIndex(0)
            self.category_list.setCurrentRow(0) # Torna su 'Tutti gli account'
            self.load_items()
            
            # Trova ed evidenzia l'elemento
            for i in range(self.items_list.count()):
                list_item = self.items_list.item(i)
                if list_item.data(Qt.ItemDataRole.UserRole) == item_id:
                    self.items_list.setCurrentItem(list_item)
                    self.display_item_details(list_item)
                    break

    def filter_by_category(self): 
        """Quando l'utente clicca una categoria, nasconde la dashboard ed apre l'interfaccia a colonne"""
        self.content_stacked_widget.setCurrentIndex(0) # Forza il ritorno alla vista a colonne
        self.load_items()
        self.clear_fields()
        self.selected_item_id = None

    def display_item_details(self, item):
        """Mostra i dettagli a destra della credenziale selezionata al centro"""
        self.content_stacked_widget.setCurrentIndex(0)
        self.selected_item_id = item.data(Qt.ItemDataRole.UserRole)
        t = next((i for i in self.db.get_items() if i["id"] == self.selected_item_id), None)
        if t:
            self.title_in.setText(t["title"])
            self.user_in.setText(t["username"])
            self.pass_in.setText(t["password"])
            self.url_in.setText(t["url"])
            self.notes_in.setText(t["notes"])
            self.cat_combo.setCurrentText(t["category"])

    def prepare_for_new_item(self): 
        self.content_stacked_widget.setCurrentIndex(0)
        self.selected_item_id = None
        self.clear_fields()
        self.title_in.setFocus()

    def trigger_logout(self):
        conferma = QMessageBox.question(
            self, "Logout", "Vuoi bloccare la cassaforte e tornare al Login?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if conferma == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()

    def update_slider_label(self, value):
        self.slider_label.setText(f"📏 Lunghezza generatore: {value} caratteri")

    def toggle_category_delete_button(self):
        selected_item = self.category_list.currentItem()
        if selected_item and selected_item.text() not in ["Tutti gli account"]:
            self.btn_delete_category.setEnabled(True)
        else:
            self.btn_delete_category.setEnabled(False)

    def delete_selected_category(self):
        selected_item = self.category_list.currentItem()
        if not selected_item:
            return
            
        category_name = selected_item.text()
        if category_name in ["Tutti gli account"]:
            return

        conferma = QMessageBox.question(
            self, "Elimina Categoria", 
            f"Eliminare la categoria '{category_name}'?\n\nLe password contrassegnate non verranno perse, ma resteranno visibili in 'Tutti gli account'.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if conferma == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_category(category_name)
                self.load_categories()
                self.load_items()
                self.btn_delete_category.setEnabled(False)
                self.open_personal_dashboard()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore: {e}")

    def load_categories(self):
        self.category_list.clear()
        self.cat_combo.clear()
        self.category_list.addItem("Tutti gli account")
        for cat in self.db.get_categories():
            if cat.lower() != "generale":
                self.category_list.addItem(cat)
                self.cat_combo.addItem(cat)

    def load_items(self):
        self.items_list.clear()
        query = self.search_bar.text().lower()
        curr_cat = self.category_list.currentItem().text() if self.category_list.currentItem() else "Tutti gli account"
        for item in self.db.get_items():
            if curr_cat != "Tutti gli account" and item["category"] != curr_cat: continue
            if query and not (query in item["title"].lower() or query in item["username"].lower()): continue
            li = QListWidgetItem(f"{item['title']} ({item['username']})")
            li.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.items_list.addItem(li)

    def clear_fields(self): 
        self.title_in.clear()
        self.user_in.clear()
        self.pass_in.clear()
        self.url_in.clear()
        self.notes_in.clear()

    def save_item(self):
        t = self.title_in.text().strip()
        u = self.user_in.text().strip()
        p = self.pass_in.text()
        url = self.url_in.text().strip()
        n = self.notes_in.toPlainText()
        c = self.cat_combo.currentText() if self.cat_combo.currentText() else ""
        if not t: return
        if self.selected_item_id: 
            self.db.update_item(self.selected_item_id, t, u, p, url, n, c)
        else: 
            self.selected_item_id = self.db.add_item(t, u, p, url, n, c)
        self.load_items()
        QMessageBox.information(self, "Salvataggio", "Dati crittografati nel Database!")
        self.open_personal_dashboard()

    def delete_item(self):
        if self.selected_item_id and QMessageBox.question(self, "Elimina", "Eliminare questa credenziale?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.delete_item(self.selected_item_id)
            self.selected_item_id = None
            self.clear_fields()
            self.load_items()
            self.open_personal_dashboard()

    def toggle_password(self, chk): 
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Normal if chk else QLineEdit.EchoMode.Password)
    
    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^*()"
        self.pass_in.setText(''.join(secrets.choice(chars) for _ in range(self.slider.value())))

    def copy_to_clipboard(self, text, secret=False):
        if not text: return
        QGuiApplication.clipboard().setText(text)
        if secret:
            self.clipboard_timer.start(15000)
            self.statusBar().showMessage("Password copiata di nascosto negli appunti!", 4000)
        else:
            self.statusBar().showMessage("Copiato!", 2000)

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Nuova Categoria", "Nome:")
        if ok and name.strip() and name.strip().lower() != "generale":
            self.db.add_category(name.strip())
            self.load_categories()

    def clear_clipboard(self): 
        QGuiApplication.clipboard().clear()
        self.statusBar().showMessage("Appunti ripuliti per sicurezza.", 3000)