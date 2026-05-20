#                                          NEL TERMINALE INSERIRE QUESTI COMANDI PER RIAVVIARE IL PROGRAMMA IN FUTURO
# cd "/Users/marcogasby/progetti visual studio/PASSW-MANAGER 2.0"
# source venv/bin/activate
# python3 main.py


import sys
import os

# Rileva se l'applicazione sta girando dentro un pacchetto chiuso (.app) o dal terminale
if getattr(sys, 'frozen', False):
    # Se è un'app compilata, i file si trovano nella cartella temporanea di PyInstaller
    current_dir = sys._MEIPASS
else:
    # Se stiamo usando il terminale, usa la cartella corrente
    current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.append(current_dir)

from PyQt6.QtWidgets import QApplication
from database.db_manager import DBManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Inizializza il database locale cercando il file nella cartella corretta dell'utente
    # Mettiamo il database nella cartella Home dell'utente per evitare problemi di permessi sul Desktop
    db_path = os.path.expanduser("~/vault.json")
    db_manager = DBManager(filename=db_path)
    
    login = LoginWindow(db_manager)
    main_win = None

    def on_login_success():
        nonlocal main_win
        main_win = MainWindow(db_manager)
        main_win.show()
        login.close()

    login.login_success.connect(on_login_success)
    login.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
