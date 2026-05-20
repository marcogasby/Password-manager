from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication

class LoginWindow(QWidget):
    login_success = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Fortress Vault - Accedi")
        
        # Calcolo dinamico per renderlo grande circa 1/4 dello schermo dell'utente
        screen = QGuiApplication.primaryScreen().geometry()
        width = int(screen.width() / 4)
        height = int(screen.height() / 2)
        self.resize(width, height)
        
        self.setStyleSheet("""
            QWidget { background-color: #16191e; color: #e3e6eb; font-family: 'Segoe UI', sans-serif; }
            QLabel#Logo { font-size: 28px; font-weight: bold; color: #4f46e5; margin-top: 20px; margin-bottom: 5px; }
            QLabel#Sub { font-size: 12px; color: #9ca3af; margin-bottom: 25px; }
            QLineEdit { background-color: #1f242d; border: 1px solid #2d3545; border-radius: 8px; padding: 12px; font-size: 14px; color: #ffffff; margin-bottom: 15px; }
            QLineEdit:focus { border: 1px solid #4f46e5; }
            QPushButton { background-color: #4f46e5; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #4338ca; }
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

        self.sub_label = QLabel("Gestione password sicura a conoscenza zero")
        self.sub_label.setObjectName("Sub")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_action)
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Conferma Master Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setVisible(False)
        layout.addWidget(self.confirm_password_input)

        self.action_btn = QPushButton("Sblocca Vault")
        self.action_btn.clicked.connect(self.handle_action)
        layout.addWidget(self.action_btn)

        self.switch_btn = QPushButton("Crea un nuovo Vault")
        self.switch_btn.setObjectName("SecondaryBtn")
        self.switch_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.switch_btn)

        self.is_setup_mode = not self.db.vault_exists()
        if self.is_setup_mode:
            self.set_setup_view()

        self.setLayout(layout)

    def set_setup_view(self):
        self.is_setup_mode = True
        self.logo_label.setText("Nuovo Vault")
        self.sub_label.setText("Crea una Master Password robusta per iniziare")
        self.confirm_password_input.setVisible(True)
        self.action_btn.setText("Inizializza Archivio")
        self.switch_btn.setVisible(False)

    def handle_action(self):
        pwd = self.password_input.text()
        if not pwd:
            QMessageBox.warning(self, "Errore", "La password non può essere vuota.")
            return

        if self.is_setup_mode:
            if pwd != self.confirm_password_input.text():
                QMessageBox.critical(self, "Errore", "Le password non coincidono.")
                return
            if len(pwd) < 8:
                QMessageBox.warning(self, "Sicurezza", "Usa almeno 8 caratteri.")
                return
            if self.db.create_vault(pwd):
                QMessageBox.information(self, "Successo", "Vault crittografato creato con successo!")
                self.login_success.emit()
        else:
            if self.db.open_vault(pwd):
                self.login_success.emit()
            else:
                QMessageBox.critical(self, "Errore", "Master Password errata.")
                self.password_input.clear()

    def toggle_mode(self):
        if not self.is_setup_mode:
            self.set_setup_view()
        else:
            self.is_setup_mode = False
            self.logo_label.setText("FORTRESS")
            self.sub_label.setText("Gestione password sicura a conoscenza zero")
            self.confirm_password_input.setVisible(False)
            self.action_btn.setText("Sblocca Vault")
            self.switch_btn.setText("Crea un nuovo Vault")

            