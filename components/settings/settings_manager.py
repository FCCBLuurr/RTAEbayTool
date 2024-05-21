import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox

class SettingsManager:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        settings_file = os.path.join(base_dir, 'settings.json')
        self.settings_manager = SettingsManager(settings_file)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Settings')
        self.setFixedSize(400, 200)

        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout()

        self.photo_dir_label = QLabel(f"Default Photo Directory: {self.settings_manager.get_setting('default_photo_directory', './photos')}", self)
        layout.addWidget(self.photo_dir_label)
        set_photo_dir_button = QPushButton('Set Default Photo Directory', self)
        set_photo_dir_button.clicked.connect(self.set_default_photo_directory)
        layout.addWidget(set_photo_dir_button)

        self.output_dir_label = QLabel(f"Default Output Directory: {self.settings_manager.get_setting('default_output_directory', './output')}", self)
        layout.addWidget(self.output_dir_label)
        set_output_dir_button = QPushButton('Set Default Output Directory', self)
        set_output_dir_button.clicked.connect(self.set_default_output_directory)
        layout.addWidget(set_output_dir_button)

        self.documents_dir_label = QLabel(f"Default Documents Directory: {self.settings_manager.get_setting('default_documents_directory', './documents')}", self)
        layout.addWidget(self.documents_dir_label)
        set_documents_dir_button = QPushButton('Set Default Documents Directory', self)
        set_documents_dir_button.clicked.connect(self.set_default_documents_directory)
        layout.addWidget(set_documents_dir_button)

        widget.setLayout(layout)

    def set_default_photo_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select default photo directory')
        if directory:
            self.settings_manager.set_setting('default_photo_directory', directory)
            self.photo_dir_label.setText(f"Default Photo Directory: {directory}")
            QMessageBox.information(self, "Settings Saved", "Default photo directory has been updated.")

    def set_default_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select default output directory')
        if directory:
            self.settings_manager.set_setting('default_output_directory', directory)
            self.output_dir_label.setText(f"Default Output Directory: {directory}")
            QMessageBox.information(self, "Settings Saved", "Default output directory has been updated.")
            
    def set_default_documents_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select default documents directory')
        if directory:
            self.settings_manager.set_setting('default_documents_directory', directory)
            self.documents_dir_label.setText(f"Default Documents Directory: {directory}")
            QMessageBox.information(self, "Settings Saved", "Default documents directory has been updated.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
