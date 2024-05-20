import os
import re

def get_file_list(folder_path):
    files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
    return files

def rename_files(folder_path, prefix, start_number, num_photos, files):
    count = start_number
    photo_index = 1
    
    # Attempt to sort files and catch any that cause an IndexError
    try:
        files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    except IndexError as e:
        for x in files:
            if not re.findall(r'\d+', x):
                print(f"File without number: {x}")  # Print out the problematic file name
        raise e  # Re-raise the exception to stop the execution and indicate the error

    total_files = len(files)
    
    for file_name in files:
        current_path = os.path.join(folder_path, file_name)
        new_name = f"{prefix}#{count}_{photo_index}.jpg"
        new_path = os.path.join(folder_path, new_name)
        os.rename(current_path, new_path)
        
        photo_index += 1
        if photo_index > num_photos:
            count += 1
            photo_index = 1
    return total_files
