import os
import shutil
from tqdm import tqdm

def handle_duplicates_delete_all(duplicate_sets, silent=False, log_file=None):
    """Deletes all duplicate files, keeping one original from each set."""
    if not silent:
        print("Deleting duplicate files...")
    for file_set in tqdm(duplicate_sets, desc="Deleting duplicates", disable=silent):
        # Keep the first file, delete the rest
        for file_to_delete in file_set[1:]:
            try:
                os.remove(file_to_delete)
                message = f"Deleted duplicate: {file_to_delete}"
                if silent and log_file:
                    with open(log_file, 'a') as f:
                        f.write(message + '\n')
                elif not silent:
                    print(message)
            except OSError as e:
                message = f"Error deleting file {file_to_delete}: {e}"
                if silent and log_file:
                    with open(log_file, 'a') as f:
                        f.write(message + '\n')
                else:
                    print(message)

def handle_duplicates_move_all(duplicate_sets, move_to_folder, silent=False, log_file=None):
    """Moves all duplicate files to a specified folder."""
    if not os.path.exists(move_to_folder):
        os.makedirs(move_to_folder)

    if not silent:
        print(f"Moving duplicate files to {move_to_folder}...")

    for file_set in tqdm(duplicate_sets, desc="Moving duplicates", disable=silent):
        # Keep the first file, move the rest
        for file_to_move in file_set[1:]:
            try:
                shutil.move(file_to_move, os.path.join(move_to_folder, os.path.basename(file_to_move)))
                message = f"Moved duplicate: {file_to_move}"
                if silent and log_file:
                    with open(log_file, 'a') as f:
                        f.write(message + '\n')
                elif not silent:
                    print(message)
            except (IOError, OSError) as e:
                message = f"Error moving file {file_to_move}: {e}"
                if silent and log_file:
                    with open(log_file, 'a') as f:
                        f.write(message + '\n')
                else:
                    print(message)

def handle_individual_duplicate(file_set, action, index_to_keep, silent=False, log_file=None):
    """Handles a single set of duplicates based on user's choice."""
    if action == 'keep_one':
        for i, file_path in enumerate(file_set):
            if i != index_to_keep:
                try:
                    os.remove(file_path)
                    message = f"Deleted duplicate: {file_path}"
                    if silent and log_file:
                        with open(log_file, 'a') as f:
                            f.write(message + '\n')
                    elif not silent:
                        print(message)
                except OSError as e:
                    message = f"Error deleting file {file_path}: {e}"
                    if silent and log_file:
                        with open(log_file, 'a') as f:
                            f.write(message + '\n')
                    else:
                        print(message)