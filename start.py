import os
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from dotenv import load_dotenv
from icecream import ic
import update

def run_script(script_name):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_folder = f"({script_name})"
        script_path = os.path.join(base_dir, "components", script_folder, script_name + ".py")
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
        self.init_ui()

    def init_ui(self):
        # Initialize buttons
        self.create_button("Step 1 \n Rename Photos", "renameScript", 0, 0)
        self.create_button("Step 2 \n Upload Photos", "uploadPhotos", 1, 0)
        self.create_button("Step 3 \n Create Payload", "extract", 2, 0)
        self.create_button("Step 3.5 \n Update Spreadsheet", "update", 2, 1)
        self.create_button("Auction Orders Only! \n Import Orders \n to Shipstation", "importShipstation", 0, 2)

    def create_button(self, text, script_name, column, row):
        button = QPushButton(text, self)
        button.clicked.connect(lambda _, sn=script_name: run_script(sn))  # Fixed lambda
        button.setFixedSize(200, 100)
        button.move(10 + (210 * column), 10 + (110 * row))

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
