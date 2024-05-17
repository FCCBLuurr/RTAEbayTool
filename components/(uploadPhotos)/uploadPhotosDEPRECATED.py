import os

# Setting environment variables for the Tcl/Tk libraries
os.environ['TCL_LIBRARY'] = '/Library/Frameworks/Tcl.framework/Versions/8.6'
os.environ['TK_LIBRARY'] = '/Library/Frameworks/Tk.framework/Versions/8.6'

import random
import platform
import json
import time
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, simpledialog, messagebox
import flickrapi
import webbrowser
from icecream import ic

class FlickrApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flickr Tool")
        self.geometry("1000x600")
        
        self.api_key = '334014b6d21d5ff73d97c9bc73339b98'
        self.api_secret = 'c12f6d81faacc343'
        self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret, format='etree')
        
        self.photos_data = {}
        self.selected_files = []  # Initialize to an empty list to ensure it's always defined
        
        if platform.system() == 'Darwin':
            self.bind('<Meta-a>', self.select_files)
        else:
            self.bind('<Control-a>', self.select_files)

        self.create_widgets()
        self.check_auth()

    def create_widgets(self):
        self.listbox = tk.Listbox(self, height=10, width=50)
        scrollbar = tk.Scrollbar(self.listbox, orient=tk.VERTICAL)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(pady=20)

        self.auth_button = tk.Button(self, text="Authenticate with Flickr", command=self.start_authentication)
        self.auth_button.pack(pady=20)

        self.file_button = tk.Button(self, text="Select Files", command=self.select_files)
        self.upload_button = tk.Button(self, text="Upload Files", command=self.upload_photos)
        self.file_button.pack(pady=10, side=tk.BOTTOM)
        self.upload_button.pack(pady=10, side=tk.BOTTOM)

    def check_auth(self):
        if not self.flickr.token_valid(perms='write'):
            self.start_authentication()
        else:
            self.toggle_widgets(True)

    def start_authentication(self):
        self.flickr.get_request_token(oauth_callback='oob')
        authorize_url = self.flickr.auth_url(perms='write')
        webbrowser.open_new_tab(authorize_url)
        verifier = simpledialog.askstring("Verifier", "Enter the verifier code from Flickr:", parent=self)
        if verifier:
            self.flickr.get_access_token(verifier)
            self.toggle_widgets(True)

    def toggle_widgets(self, show_upload):
        if show_upload:
            self.auth_button.pack_forget()
            self.listbox.pack(pady=20)  # Show the listbox
            self.file_button.pack(side=tk.BOTTOM)
            self.upload_button.pack(side=tk.BOTTOM)
        else:
            self.listbox.pack_forget()  # Hide the listbox
            self.file_button.pack_forget()
            self.upload_button.pack_forget()
            self.auth_button.pack()

    def select_files(self):
        initial_dir = '/Users/ejrta/Pictures/Test'
        self.selected_files = filedialog.askopenfilenames(title="Choose files",
                                                        initialdir=initial_dir,
                                                        filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*")])
        self.listbox.delete(0, tk.END)  # Clear existing entries in the listbox
        for file in self.selected_files:
            self.listbox.insert(tk.END, os.path.basename(file))

    def upload_photos(self):
        # Path selection debug
        initial_dir = self.selected_files[0] if self.selected_files else '/Users/ejrta/Pictures/Test'
        file_path = filedialog.askdirectory(title="Select folder containing photos", initialdir=initial_dir)
        if not file_path:
            ic("No folder selected.")
            return

        # File filtering debug
        valid_extensions = ('.jpg', '.jpeg', '.png')
        files_to_upload = sorted([os.path.join(file_path, f) for f in os.listdir(file_path)
                                if os.path.isfile(os.path.join(file_path, f)) and f.lower().endswith(valid_extensions)])
        ic("Files to upload:", files_to_upload)

        if not files_to_upload:
            ic("No files to upload found. Check file types and paths.")
            return
        for file_path in files_to_upload:
            filename = os.path.basename(file_path)
            sku, suffix = self.parse_filename(filename)
            ic("Attempting to upload file:", filename)

            retries = 0
            max_retries = 3
            while retries < max_retries:
                try:
                    response = self.flickr.upload(filename=file_path, title=filename)
                    photo_id = response.find('photoid').text
                    if photo_id:
                        url = self.retrieve_photo_url(photo_id)
                        self.add_photo_data(sku, suffix, url)
                        ic("Upload successful for:", filename, "Photo ID:", photo_id)
                        break
                    else:
                        raise Exception("No Photo ID returned")
                except Exception as e:
                    ic(f"Failed to upload {filename} on attempt {retries + 1}/{max_retries}. Error:", str(e))
                    retries += 1
                    if retries >= max_retries:
                        ic("Max retries reached for:", filename)
                    time.sleep(5)  # Wait for 5 seconds before retrying

        self.write_json()

    def parse_filename(self, filename):
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('#')
        if len(parts) < 2:
            return None, None
        
        sku_part = parts[1]
        sku_parts = sku_part.split('_')
        if len(sku_parts) < 2:
            return None, None
        
        sku = sku_parts[0]
        suffix = sku_parts[1]
        ic("SKU: ", sku)
        return sku, suffix
    
    
    def retrieve_photo_url(self, photo_id):
        sizes = self.flickr.photos.getSizes(photo_id=photo_id)
        url = sizes.find('.//size[@label="Original"]').get('source')
        return url

    def add_photo_data(self, sku, suffix, url):
        if sku not in self.photos_data:
            self.photos_data[sku] = []
        self.photos_data[sku].append((str(suffix), url))

    def write_json(self):
        organized_data = {}
        for sku, urls in self.photos_data.items():
            sorted_urls = sorted(urls, key=lambda x: x[0])
            organized_data[sku] = {'url': '|'.join([url for _, url in sorted_urls])}

        target_path = '/Users/ejrta/Documents/Coding Folders/Scripts and Macros/Tools and Workflow Scripts/Flickr&Ebay/components/(extract)/photos.json'
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))
        
        with open(target_path, 'w') as json_file:
            json.dump({'photos': organized_data}, json_file, indent=4)

        ic(f"Photos JSON saved to: ", target_path)

if __name__ == '__main__':
    app = FlickrApp()
    app.mainloop()
