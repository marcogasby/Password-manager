from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication

class LoginWindow(QWidget):
    # Passiamo sia il db_manager che il nome utente finale al segnale di successo
    login_success = pyqtSignal(str) 

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Fortress - Accedi")
        
        # Calcolo dinamico per renderlo grande circa 1/4 dello schermo dell'utente
        screen = QGuiApplication.primaryScreen().geometry()
        width = int(screen.width() / 4)
        height = int(screen.height() / 1.8)
        self.resize(width, height)
        
        # Aggiornata la palette: rimosso l'indigo ed esteso il look Fortress coordinato
        self.setStyleSheet("""
            QWidget { background-color: #16191e; color: #e3e6eb; font-family: 'Segoe UI', sans-serif; }
            QLabel#Logo { font-size: 28px; font-weight: bold; color: #1f6feb; margin-top: 20px; margin-bottom: 5px; }
            QLabel#Sub { font-size: 12px; color: #9ca3af; margin-bottom: 25px; }
            QLineEdit { background-color: #1f242d; border: 1px solid #2d3545; border-radius: 8px; padding: 12px; font-size: 14px; color: #ffffff; margin-bottom: 15px; }
            QLineEdit:focus { border: 1px solid #1f6feb; }
            QPushButton { background-color: #238636; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #2ea043; }
            QPushButton#SecondaryBtn { background-color: transparent; color: #9ca3af; font-weight: normal; font-size: 13px; }
            QPushButton#SecondaryBtn:hover { color: #ffffff; }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        self.logo_label = QLabel("FORTRESS")
        self.logo_label.setObjectName("Logo")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        # GESTORE DI PASSWORD BY MARCO GASBY CON EVIDENZIAZIONE GIALLA SUL NOME
        self.sub_label = QLabel()
        self.sub_label.setObjectName("Sub")
        self.sub_label.setTextFormat(Qt.TextFormat.RichText) # Permette l'uso di HTML per lo stile parziale
        self.sub_label.setText('Gestore di password by <span style="color: #ffb703; font-weight: bold;">Marco Gasby</span>')
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        # NUOVO CAMPO: Master Name (Username)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Master Name (Nome Utente)")
        self.username_input.returnPressed.connect(self.handle_action)
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_action)
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Conferma Master Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.returnPressed.connect(self.handle_action)
        self.confirm_password_input.setVisible(False)
        layout.addWidget(self.confirm_password_input)

        self.action_btn = QPushButton("Sblocca Vault")
        self.action_btn.clicked.connect(self.handle_action)
        layout.addWidget(self.action_btn)

        self.switch_btn = QPushButton("Registra nuovo utente / Crea Vault")
        self.switch_btn.setObjectName("SecondaryBtn")
        self.switch_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.switch_btn)

        # Di default partiamo in modalità Login standard
        self.is_setup_mode = False

        self.setLayout(layout)

    def set_setup_view(self):
        self.is_setup_mode = True
        self.logo_label.setText("Nuovo Utente")
        self.confirm_password_input.setVisible(True)
        self.action_btn.setText("Registrati e Inizializza")
        self.switch_btn.setText("Hai già un account? Accedi")

    def handle_action(self):
        username = self.username_input.text().strip()
        pwd = self.password_input.text()

        if not username:
            QMessageBox.warning(self, "Errore", "Il Master Name non può essere vuoto.")
            return
        if not pwd:
            QMessageBox.warning(self, "Errore", "La password non può essere vuota.")
            return

        # Configura dinamicamente il file basandosi sul Master Name inserito
        import os
        db_path = os.path.expanduser(f"~/vault_{username}.json")
        self.db.filename = db_path

        if self.is_setup_mode:
            if os.path.exists(db_path):
                QMessageBox.warning(self, "Errore", f"L'utente '{username}' esiste già su questo computer.")
                return
            if pwd != self.confirm_password_input.text():
                QMessageBox.critical(self, "Errore", "Le password non coincidono.")
                return
                
            if len(pwd) < 8:
                QMessageBox.warning(self, "Sicurezza", "Usa almeno 8 caratteri per la password.")
                return
                
            if self.db.create_vault(pwd):
                QMessageBox.information(self, "Successo", f"Vault per l'utente '{username}' creato con successo!")
                self.login_success.emit(username)
        else:
            if not os.path.exists(db_path):
                QMessageBox.critical(self, "Errore", f"L'utente '{username}' non esiste. Registrati prima.")
                return
                
            if self.db.open_vault(pwd):
                self.login_success.emit(username)
            else:
                QMessageBox.critical(self, "Errore", "Master Password errata.")
                self.password_input.clear()

    def toggle_mode(self):
        if not self.is_setup_mode:
            self.set_setup_view()
        else:
            self.is_setup_mode = False
            self.logo_label.setText("FORTRESS")
            self.confirm_password_input.setVisible(False)
            self.action_btn.setText("Sblocca Vault")
            self.switch_btn.setText("Registra nuovo utente / Crea Vault")