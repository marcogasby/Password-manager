#                                          NEL TERMINALE INSERIRE QUESTI COMANDI PER RIAVVIARE IL PROGRAMMA IN FUTURO
# cd "/Users/marcogasby/progetti visual studio/PASSW-MANAGER 2.0"
# source venv/bin/activate
# python3 main.py




import sys
import os

if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.append(current_dir)

from PyQt6.QtWidgets import QApplication
from database.db_manager import DBManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Iniziamo con un'istanza vuota, il file corretto verrà impostato dinamicamente al login
    db_manager = DBManager(filename="")
    
    login = LoginWindow(db_manager)
    main_win = None

    def on_login_success(logged_user):
        nonlocal main_win
        # Passiamo SIA il db_manager SIA il nome dell'utente loggato alla MainWindow
        main_win = MainWindow(db_manager, logged_user)
        main_win.logout_requested.connect(on_logout)
        main_win.show()
        login.close()

    def on_logout():
        nonlocal main_win
        if main_win:
            main_win.close()
            main_win = None
        
        db_manager.active_data = None
        
        nonlocal login
        login = LoginWindow(db_manager)
        login.login_success.connect(on_login_success)
        login.show()

    login.login_success.connect(on_login_success)
    login.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()