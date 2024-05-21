import os
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QMenuBar, QMenu, QAction, QFileDialog
from dotenv import load_dotenv
from icecream import ic
import update
from components.settings.settings_manager import SettingsManager


def run_script(script_name):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_folder = f"components/({script_name})"
        script_path = os.path.join(base_dir, script_folder, script_name + ".py")
        subprocess.run(["python3", script_path], check=True)
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(None, "Error", f"Failed to run {script_name}.\n{str(e)}")

def git_pull():
    try:
        # Fetch the latest changes from the remote repository
        fetch_result = subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True, text=True)
        ic(fetch_result.stdout)
        ic(fetch_result.stderr)

        # Reset the local branch to match the remote branch
        reset_result = subprocess.run(["git", "reset", "--hard", "origin/main"], check=True, capture_output=True, text=True)
        ic(reset_result.stdout)
        ic(reset_result.stderr)

        return fetch_result.returncode == 0 and reset_result.returncode == 0
    except subprocess.CalledProcessError as e:
        ic(e.stdout)
        ic(e.stderr)
        return False

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("~~Alpha Test~~")
        self.setFixedHeight(350)
        self.setFixedWidth(640)
        settings_file = os.path.join(os.path.dirname(__file__), 'components', 'settings', 'settings.json')
        self.settings_manager = SettingsManager(settings_file)
        self.init_ui()

    def init_ui(self):
        # Initialize menu bar
        menu_bar = self.menuBar()

        # Create Settings menu
        settings_menu = QMenu("Settings", self)
        menu_bar.addMenu(settings_menu)

        # Add action to Settings menu
        open_settings_action = QAction("Open Settings", self)
        open_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(open_settings_action)
        
        # Initialize buttons
        self.create_button("Step 1 \n Rename Photos", "renameScript", 0, 0)
        self.create_button("Step 2 \n Upload Photos", "uploadPhotos", 1, 0)
        self.create_button("Step 3 \n Create Payload", "extract", 2, 0)
        # self.create_button("Step 3.5 \n Update Spreadsheet", "updateSS", 2, 1)
        self.create_button("Auction Orders Only! \n Import Orders \n to Shipstation", "importShipstation", 0, 2)

    def create_button(self, text, script_name, column, row):
        button = QPushButton(text, self)
        button.clicked.connect(lambda _, sn=script_name: run_script(sn))  # Fixed lambda
        button.setFixedSize(200, 100)
        #Moved buttons down 15 pixels to accomodate for the settings bar
        button.move(10 + (210 * column), 25 + (110 * row))
        
    
    def set_default_paths(self):
        photo_directory = QFileDialog.getExistingDirectory(self, 'Select default photo directory')
        if photo_directory:
            self.settings_manager.set_setting('default_photo_directory', photo_directory)
        
        output_directory = QFileDialog.getExistingDirectory(self, 'Select default output directory')
        if output_directory:
            self.settings_manager.set_setting('default_output_directory', output_directory)
        
        QMessageBox.information(self, "Settings Saved", "Default paths have been updated.")

    ## Change to "python" when pushing to git
    def open_settings(self):
        subprocess.run(["python3", "components/settings/settings_manager.py"], check=True)
    
if __name__ == "__main__":
    load_dotenv()
    current_version = os.getenv('VERSION')
    ic("Current Version: ", current_version)

    # Check for updates before starting the main application window
    update_available, new_version = update.check_for_updates(current_version)

    if update_available:
        app = QApplication([])  # Create QApplication instance for QMessageBox
        QMessageBox.information(None, "Update Available", f"A new version {new_version} is available.")
        if git_pull():
            with open('.env', 'r') as file:
                lines = file.readlines()
            with open('.env', 'w') as file:
                for line in lines:
                    if line.startswith("VERSION"):
                        file.write(f"VERSION={new_version}\n")
                    else:
                        file.write(line)
            QMessageBox.information(None, "Update Complete", "The application has been updated to the latest version. Please restart the application.")
        else:
            QMessageBox.critical(None, "Update Failed", "The update process failed. Please check the logs.")
        app.quit()  # Close the application to prompt a restart
    else:
        app = QApplication([])
        window = App()
        window.show()
        app.exec_()
