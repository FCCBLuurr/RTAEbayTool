import os
import shutil
from tkinter import Tk
from tkinter import filedialog

def setup_user_interface():
    # Initialize Tkinter
    root = Tk()
    root.withdraw()  # Hide the main window

    # Ask the user to select the source directory
    source_dir = filedialog.askdirectory(title='Select Source Directory')
    if not source_dir:
        print("No source directory selected, exiting.")
        exit()

    # Ask the user to select the payload.txt file
    sku_file = "./payload.txt"
    # sku_file = filedialog.askopenfilename(title='Select SKU File', filetypes=[('Text files', '*.txt')])
    if not sku_file:
        print("No SKU file selected, exiting.")
        exit()
    
    destination_dir = filedialog.askdirectory(title='Select Destination Directory')
    if not destination_dir:
        print('No destination Directory chosen')
        exit()

    return source_dir, sku_file, destination_dir

def copy_files_for_skus(source_dir, sku_file, destination_dir):
    # Read SKUs from file
    with open(sku_file, 'r') as f:
        skus = [line.strip() for line in f.readlines() if line.strip()]

    print(f"SKUs to process: {skus}")

    copied_files = set()  # Set to track copied files
    all_skus_copied = set()  # Set to track SKUs for which all files have been copied

    for root, _, files in os.walk(source_dir):
        for file in files:
            print(f'Found file: {file}')  # Print every file found
            for sku in skus:
                sku_copied = False
                for prefix in ['GCE#', 'RTA#', 'GCE_', 'RTA_']:
                    for suffix in ['_1', '_2', '_3', '_4']:
                        # for file_type in [ 'jpg', 'JPG', 'jpeg', 'JPEG']:
                        # for file_type in ['jpg', 'JPG']:
                        for file_type in ['jpg', 'JPG', 'jpeg', 'JPEG', 'CR2', 'CR3']:
                            filename = f'{prefix}{sku}{suffix}.{file_type}'
                            if file == filename:
                                print(f'Attempting to copy: {filename}')  # Print the file being processed
                                source_path = os.path.join(root, filename)
                                destination_path = os.path.join(destination_dir, filename)
                                if source_path == destination_path:
                                    print(f'Skipping: Source and destination are the same for {filename}')
                                    continue
                                try:
                                    if filename not in copied_files:
                                        shutil.copy2(source_path, destination_path)
                                        print(f'Copied: {filename}')
                                        copied_files.add(filename)
                                        sku_copied = True
                                except Exception as e:
                                    print(f"Error copying {filename}: {e}")
                                if sku_copied:
                                    all_skus_copied.add(sku)  # Track SKUs for which at least one file has been copied

    remaining_skus = [sku for sku in skus if sku not in all_skus_copied]

    # Update SKUs in payload.txt with those that weren't fully processed
    with open(sku_file, 'w') as f:
        for sku in remaining_skus:
            f.write(sku + '\n')

    print(f"Updated payload.txt with remaining SKUs: {remaining_skus}")

if __name__ == "__main__":
    source_dir, sku_file, destination_dir = setup_user_interface()
    copy_files_for_skus(source_dir, sku_file, destination_dir)
