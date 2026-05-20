import secrets
import string
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLineEdit, QLabel, 
                             QPushButton, QTextEdit, QComboBox, QInputDialog, 
                             QMessageBox, QSlider)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.selected_item_id = None
        self.clipboard_timer = QTimer()
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.timeout.connect(self.clear_clipboard)
        self.init_ui()
        self.load_categories()
        self.load_items()

    def init_ui(self):
        self.setWindowTitle("Fortress Vault")
        self.resize(1000, 600)
        
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            QListWidget { background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 5px; }
            QListWidget::item { padding: 10px; border-radius: 4px; }
            QListWidget::item:selected { background-color: #1f6feb; color: white; }
            QLineEdit, QTextEdit, QComboBox { background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 8px; color: #f0f6fc; }
            QPushButton { background-color: #21262d; border: 1px solid #30363d; border-radius: 6px; padding: 8px 15px; color: #c9d1d9; font-weight: bold; }
            QPushButton:hover { background-color: #30363d; }
            QPushButton#AccentBtn { background-color: #238636; border: 1px solid #2ea043; color: white; }
            QPushButton#AccentBtn:hover { background-color: #2ea043; }
            QPushButton#DangerBtn { background-color: #da3637; color: white; border: none; }
            QPushButton#DangerBtn:hover { background-color: #f85149; }
        """)

        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)

        # Categorie (Sinistra)
        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("CATEGORIE"))
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.filter_by_category)
        sidebar.addWidget(self.category_list)
        add_cat_btn = QPushButton("+ Categoria")
        add_cat_btn.clicked.connect(self.add_category)
        sidebar.addWidget(add_cat_btn)
        layout.addLayout(sidebar, stretch=2)

        # Lista Elementi (Centro)
        center = QVBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Cerca...")
        self.search_bar.textChanged.connect(self.load_items)
        center.addWidget(self.search_bar)
        self.items_list = QListWidget()
        self.items_list.itemClicked.connect(self.display_item_details)
        center.addWidget(self.items_list)
        new_btn = QPushButton("+ Aggiungi Account")
        new_btn.setObjectName("AccentBtn")
        new_btn.clicked.connect(self.prepare_for_new_item)
        center.addWidget(new_btn)
        layout.addLayout(center, stretch=3)

        # Modulo Dettagli (Destra)
        details = QVBoxLayout()
        self.title_in = QLineEdit()
        self.user_in = QLineEdit()
        self.pass_in = QLineEdit()
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        self.url_in = QLineEdit()
        self.notes_in = QTextEdit()
        self.cat_combo = QComboBox()

        details.addWidget(QLabel("Servizio:"))
        details.addWidget(self.title_in)
        details.addWidget(QLabel("Username/Email:"))
        
        u_lay = QHBoxLayout(); u_lay.addWidget(self.user_in)
        c_u = QPushButton("Copia"); c_u.clicked.connect(lambda: self.copy_to_clipboard(self.user_in.text()))
        u_lay.addWidget(c_u); details.addLayout(u_lay)

        details.addWidget(QLabel("Password:"))
        p_lay = QHBoxLayout(); p_lay.addWidget(self.pass_in)
        t_p = QPushButton("👁️"); t_p.setCheckable(True); t_p.clicked.connect(self.toggle_password)
        c_p = QPushButton("Copia"); c_p.clicked.connect(lambda: self.copy_to_clipboard(self.pass_in.text(), True))
        p_lay.addWidget(t_p); p_lay.addWidget(c_p); details.addLayout(p_lay)

        # Generatore rapido
        gen_lay = QHBoxLayout()
        self.slider = QSlider(Qt.Orientation.Horizontal); self.slider.setRange(8, 32); self.slider.setValue(16)
        g_btn = QPushButton("Genera"); g_btn.clicked.connect(self.generate_password)
        gen_lay.addWidget(self.slider); gen_lay.addWidget(g_btn); details.addLayout(gen_lay)

        details.addWidget(QLabel("URL:"))
        details.addWidget(self.url_in)
        details.addWidget(QLabel("Categoria:"))
        details.addWidget(self.cat_combo)
        details.addWidget(QLabel("Note:"))
        details.addWidget(self.notes_in)

        act_lay = QHBoxLayout()
        self.save_btn = QPushButton("Salva"); self.save_btn.setObjectName("AccentBtn"); self.save_btn.clicked.connect(self.save_item)
        self.del_btn = QPushButton("Elimina"); self.del_btn.setObjectName("DangerBtn"); self.del_btn.clicked.connect(self.delete_item)
        act_lay.addWidget(self.save_btn); act_lay.addWidget(self.del_btn); details.addLayout(act_lay)

        layout.addLayout(details, stretch=4)
        self.setCentralWidget(main_widget)

    def load_categories(self):
        self.category_list.clear(); self.cat_combo.clear()
        self.category_list.addItem("🌟 Tutti gli account")
        for cat in self.db.get_categories():
            self.category_list.addItem(cat)
            self.cat_combo.addItem(cat)
        self.category_list.setCurrentRow(0)

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Nuova Categoria", "Nome:")
        if ok and name.strip():
            self.db.add_category(name.strip())
            self.load_categories()

    def load_items(self):
        self.items_list.clear()
        query = self.search_bar.text().lower()
        curr_cat = self.category_list.currentItem().text() if self.category_list.currentItem() else "🌟 Tutti gli account"
        for item in self.db.get_items():
            if curr_cat != "🌟 Tutti gli account" and item["category"] != curr_cat: continue
            if query and not (query in item["title"].lower() or query in item["username"].lower()): continue
            li = QListWidgetItem(f"{item['title']} ({item['username']})")
            li.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.items_list.addItem(li)

    def filter_by_category(self): self.load_items(); self.clear_fields()
    
    def display_item_details(self, item):
        self.selected_item_id = item.data(Qt.ItemDataRole.UserRole)
        t = next((i for i in self.db.get_items() if i["id"] == self.selected_item_id), None)
        if t:
            self.title_in.setText(t["title"]); self.user_in.setText(t["username"])
            self.pass_in.setText(t["password"]); self.url_in.setText(t["url"])
            self.notes_in.setText(t["notes"])
            self.cat_combo.setCurrentText(t["category"])

    def prepare_for_new_item(self): self.selected_item_id = None; self.clear_fields(); self.title_in.setFocus()
    def clear_fields(self): self.title_in.clear(); self.user_in.clear(); self.pass_in.clear(); self.url_in.clear(); self.notes_in.clear()

    def save_item(self):
        t, u, p, url, n, c = self.title_in.text().strip(), self.user_in.text().strip(), self.pass_in.text(), self.url_in.text().strip(), self.notes_in.toPlainText(), self.cat_combo.currentText()
        if not t: return
        if self.selected_item_id: self.db.update_item(self.selected_item_id, t, u, p, url, n, c)
        else: self.selected_item_id = self.db.add_item(t, u, p, url, n, c)
        self.load_items()
        QMessageBox.information(self, "Ok", "Dati salvati e criptati!")

    def delete_item(self):
        if self.selected_item_id and QMessageBox.question(self, "?", "Eliminare?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.delete_item(self.selected_item_id)
            self.selected_item_id = None; self.clear_fields(); self.load_items()

    def toggle_password(self, chk): self.pass_in.setEchoMode(QLineEdit.EchoMode.Normal if chk else QLineEdit.EchoMode.Password)
    
    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^*()"
        self.pass_in.setText(''.join(secrets.choice(chars) for _ in range(self.slider.value())))

    def copy_to_clipboard(self, text, secret=False):
        if not text: return
        QGuiApplication.clipboard().setText(text)
        if secret:
            self.clipboard_timer.start(15000)
            self.statusBar().showMessage("Password copiata! Sparirà tra 15 secondi.", 4000)
        else:
            self.statusBar().showMessage("Copiato!", 2000)

    def clear_clipboard(self): QGuiApplication.clipboard().clear(); self.statusBar().showMessage("Appunti svuotati.", 3000)

    