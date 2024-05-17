import os
import re

def get_file_list(folder_path):
    files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
    return files

def rename_files(folder_path, start_number, files):
    count = start_number
    i = 1
    
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
        # Generate the new file names with i iterating and resetting
        
        if i == 1:
            # new_name_1 = f"RTA#{count}_{i}.CR3"
            new_name_1 = f"RTA#{count}_1.jpg"
            current_path = os.path.join(folder_path, file_name)
            new_path_1 = os.path.join(folder_path, new_name_1)
            os.rename(current_path, new_path_1)
            i += 1
        elif i == 2:
            # new_name_2 = f"RTA#{count}_{i}.CR3"
            new_name_2 = f"RTA#{count}_2.jpg"
            current_path = os.path.join(folder_path, file_name)
            new_path_2 = os.path.join(folder_path, new_name_2)
            os.rename(current_path, new_path_2)
            count += 1
            i = 1
        
    return total_files
