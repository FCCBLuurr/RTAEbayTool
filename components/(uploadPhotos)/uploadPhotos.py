import os
import sys
import webbrowser
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QVBoxLayout, QFileDialog, QMessageBox, QWidget
from PyQt5.QtCore import Qt
import flickrapi
from icecream import ic
import random
import time
import xml.etree.ElementTree as ET
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings.settings_manager import SettingsManager
import psycopg2

# Initialize the SettingsManager with the correct path to the settings.json file
settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings', 'settings.json')
settings_manager = SettingsManager(settings_file)

default_photo_directory = settings_manager.get_setting('default_photo_directory', './photos')

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
base_dir = os.path.join(project_root, 'components')

class FlickrApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Flickr Tool')
        self.setGeometry(300, 300, 1000, 600)
        
        # API setup
        self.api_key = '334014b6d21d5ff73d97c9bc73339b98'
        self.api_secret = 'c12f6d81faacc343'
        self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret, format='etree')
        
        self.photos_data = {}
        
        # Main layout
        layout = QVBoxLayout()

        # List widget for displaying files
        self.listbox = QListWidget(self)
        layout.addWidget(self.listbox)

        # Buttons
        self.auth_button = QPushButton('Authenticate with Flickr', self)
        self.auth_button.clicked.connect(self.start_authentication)
        layout.addWidget(self.auth_button)

        # self.file_button = QPushButton('Select Files', self)
        # self.file_button.clicked.connect(self.select_files)
        # layout.addWidget(self.file_button)

        self.upload_button = QPushButton('Upload Files', self)
        self.upload_button.clicked.connect(self.upload_photos)
        layout.addWidget(self.upload_button)

        # Set the central widget
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.check_auth()

    def check_auth(self):
        if not self.flickr.token_valid(perms='write'):
            self.start_authentication()

    def start_authentication(self):
        self.flickr.get_request_token(oauth_callback='oob')
        authorize_url = self.flickr.auth_url(perms='write')
        webbrowser.open_new_tab(authorize_url)
        verifier, ok = QFileDialog.getText(self, "Verifier", "Enter the verifier code from Flickr:")
        if ok and verifier:
            self.flickr.get_access_token(verifier)
                
    def upload_photos(self):
        app = QApplication(sys.argv)  # Ensure a QApplication instance is created
        file_path = QFileDialog.getExistingDirectory(None, "Select folder containing photos", default_photo_directory, QFileDialog.ShowDirsOnly)
        if not file_path:
            return  # User cancelled the operation

        # Define the file types you want to process
        valid_extensions = ('.jpg', '.jpeg', '.png')

        # List all files in the selected directory that match the valid file types
        files_to_upload = [os.path.join(file_path, f) for f in os.listdir(file_path)
                        if os.path.isfile(os.path.join(file_path, f)) and f.lower().endswith(valid_extensions)]

        # Process each file in the list
        for file_path in files_to_upload:
            filename = os.path.basename(file_path)
            sku, suffix = self.parse_filename(filename)
            if sku and suffix:
                try:
                    response = self.flickr.upload(filename=file_path, title=filename)
                    photo_id = response.find('photoid').text
                    url = self.retrieve_photo_url(photo_id)
                    self.add_photo_data(sku, suffix, url)
                    print(f"Uploaded {filename} successfully!")
                except Exception as e:
                    print("Failed to upload", filename, "Error:", e)

        self.write_json()
        self.update_database()  # Update the database after writing JSON
        app.exit()

    def parse_filename(self, filename):
        # Assuming the filename format is `{prefix}#{sku}_{suffix}.jpg`
        base_name = os.path.splitext(filename)[0]  # Remove the .jpg
        parts = base_name.split('#')
        if len(parts) < 2:
            return None, None  # Not a valid format

        sku_part = parts[1]
        sku_parts = sku_part.split('_')
        if len(sku_parts) < 2:
            return None, None  # Not a valid format

        sku = sku_parts[0]
        suffix = sku_parts[1]
        return sku, suffix
    
    def retrieve_photo_url(self, photo_id):
        # Fetch the URL; this assumes you can directly get the URL from the API response
        sizes = self.flickr.photos.getSizes(photo_id=photo_id)
        url = sizes.find('.//size[@label="Original"]').get('source')
        return url

    def add_photo_data(self, sku, suffix, url):
        if sku not in self.photos_data:
            self.photos_data[sku] = []
        self.photos_data[sku].append((str(suffix), url))  # Store with suffix for sorting

    def write_json(self):
        # Organize and write to JSON
        organized_data_db = {}
        organized_data_file = {}
        for sku, urls in self.photos_data.items():
            sorted_urls = sorted(urls, key=lambda x: x[0])  # Sort by suffix
            organized_data_db[sku] = {'url': json.dumps([url for _, url in sorted_urls])}  # Convert to JSON array for DB
            organized_data_file[sku] = {'url': '|'.join([url for _, url in sorted_urls])}  # Concatenate URLs for file

        # Store the organized data for database update
        self.json_data = {'photos': organized_data_db}
        print("Photos JSON prepared for database update")

        # Write the organized data to a JSON file
        target_path = os.path.join(base_dir, '(extract)', 'photos.json')

        # Check if the target directory exists and create it if not
        target_directory = os.path.dirname(target_path)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        with open(target_path, 'w') as json_file:
            json.dump({'photos': organized_data_file}, json_file, indent=4)

        print(f"Photos JSON saved to {target_path}")
        return self.json_data

    def update_database(self):
        # Setup the database connection
        connection = psycopg2.connect(
            dbname="postgres",
            user="bluurr",
            password="548406",
            host="127.0.0.1",
            port="5432"
        )
        cursor = connection.cursor()

        for sku, data in self.json_data['photos'].items():
            # Check if the SKU exists in the database
            cursor.execute('SELECT sku FROM inventory.obt_inventory WHERE sku = %s', (sku,))
            row = cursor.fetchone()
            if row:
                # Update the URL for the existing SKU
                cursor.execute('UPDATE inventory.obt_inventory SET photos = %s WHERE sku = %s', (data['url'], sku))
                print(f"Updated SKU {sku} with URL {data['url']}")
            else:
                # Optionally, handle the case where SKU does not exist
                print(f"SKU {sku} does not exist in the database")
        connection.commit()

        # Print out the updated database content for verification
        cursor.execute('SELECT * FROM inventory.obt_inventory')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        # Close the database connection
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FlickrApp()
    ex.show()
    sys.exit(app.exec_())
