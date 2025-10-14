import os

def get_main_menu_selection():
    """Prompt the user to select the main operation mode."""
    while True:
        print("\n" + "="*50)
        print(" " * 15 + "MAIN MENU")
        print("="*50)
        print("Please choose an option:")
        print("1. Organize a Directory (One-time organization)")
        print("2. Watch a Directory (Continuous organization)")
        print("3. Find and Handle Duplicates")
        print("4. Exit")
        print("-"*50)
        response = input("Enter 1, 2, 3, or 4: ").strip()
        if response == '1':
            return 'organize'
        elif response == '2':
            return 'watch'
        elif response == '3':
            return 'duplicates'
        elif response == '4':
            return 'exit'
        else:
            print("Invalid selection. Please enter 1, 2, 3, or 4.")

def get_yes_no(prompt):
    """Prompt the user for a yes/no response."""
    while True:
        response = input(prompt).strip().lower()
        if response in ('yes', 'y'):
            return True
        elif response in ('no', 'n'):
            return False
        elif response == '/exit':
            print("Exiting program.")
            exit()
        else:
            print("Please enter 'yes' or 'no'. To exit, type '/exit'.")

def get_main_menu_selection():
    """Prompt the user to select the main operation mode."""
    while True:
        print("Main Menu:")
        print("1. One-time Organization")
        print("2. Watch Folder (Continuous Organization)")
        print("3. Exit")
        response = input("Enter 1, 2, or 3: ").strip()
        if response == '1':
            return 'one-time'
        elif response == '2':
            return 'watch'
        elif response == '3':
            return 'exit'
        else:
            print("Invalid selection. Please enter 1, 2, or 3.")

def get_ai_backend_selection():
    """Prompt the user to select an AI backend."""
    while True:
        print("Please choose the AI backend to use:")
        print("1. Ollama")
        print("2. Local GGUF")
        response = input("Enter 1 or 2: ").strip()
        if response == '1':
            return 'Ollama'
        elif response == '2':
            return 'Local GGUF'
        else:
            print("Invalid selection. Please enter 1 or 2.")

def get_mode_selection():
    """Prompt the user to select a mode."""
    while True:
        print("Please choose the mode to organize your files:")
        print("1. By Content")
        print("2. By Date")
        print("3. By Type")
        response = input("Enter 1, 2, or 3 (or type '/exit' to exit): ").strip()
        if response == '/exit':
            print("Exiting program.")
            exit()
        elif response == '1':
            return 'content'
        elif response == '2':
            return 'date'
        elif response == '3':
            return 'type'
        else:
            print("Invalid selection. Please enter 1, 2, or 3. To exit, type '/exit'.")

def get_paths(silent_mode, log_file):
    """Get input and output paths from the user."""
    if not silent_mode:
        print("-" * 50)

    input_path = input("Enter the path of the directory you want to organize: ").strip()
    while not os.path.exists(input_path):
        message = f"Input path {input_path} does not exist. Please enter a valid path."
        if silent_mode:
            with open(log_file, 'a') as f:
                f.write(message + '\n')
        else:
            print(message)
        input_path = input("Enter the path of the directory you want to organize: ").strip()

    message = f"Input path successfully uploaded: {input_path}"
    if silent_mode:
        with open(log_file, 'a') as f:
            f.write(message + '\n')
    else:
        print(message)
    if not silent_mode:
        print("-" * 50)

    output_path = input("Enter the path to store organized files and folders (press Enter to use 'organized_folder' in the input directory): ").strip()
    if not output_path:
        output_path = os.path.join(os.path.dirname(input_path), 'organized_folder')

    message = f"Output path successfully set to: {output_path}"
    if silent_mode:
        with open(log_file, 'a') as f:
            f.write(message + '\n')
    else:
        print(message)
    if not silent_mode:
        print("-" * 50)

    return input_path, output_path

def print_simulated_tree(tree, prefix=''):
    """Print the simulated directory tree."""
    pointers = ['├── '] * (len(tree) - 1) + ['└── '] if tree else []
    for pointer, key in zip(pointers, tree):
        print(prefix + pointer + key)
        if tree[key]:
            extension = '│   ' if pointer == '├── ' else '    '
            print_simulated_tree(tree[key], prefix + extension)

def display_duplicates(duplicate_sets):
    """Displays the sets of duplicate files found."""
    if not duplicate_sets:
        print("No duplicate files found.")
        return

    print("\n" + "="*50)
    print(" " * 15 + "DUPLICATE FILES FOUND")
    print("="*50)
    for i, file_set in enumerate(duplicate_sets, 1):
        print(f"\n--- Set {i} ---")
        for file_path in file_set:
            print(f"  - {file_path}")
    print("\n" + "="*50)

def get_duplicate_handling_choice():
    """Prompts the user for how to handle duplicates."""
    while True:
        print("\nHow would you like to handle these duplicates?")
        print("1. Delete all duplicates (keeps one original of each set)")
        print("2. Move all duplicates to a separate folder")
        print("3. Decide for each set individually")
        print("4. Do nothing (skip)")
        response = input("Enter 1, 2, 3, or 4: ").strip()
        if response == '1':
            return 'delete_all'
        elif response == '2':
            return 'move_all'
        elif response == '3':
            return 'decide_each'
        elif response == '4':
            return 'skip'
        else:
            print("Invalid selection. Please enter 1, 2, 3, or 4.")

def get_individual_duplicate_action(file_set):
    """Prompts the user for action on an individual set of duplicates."""
    while True:
        print("\n--- Processing Set ---")
        for i, file_path in enumerate(file_set):
            print(f"{i+1}. {file_path}")

        print("\nChoose an action for this set:")
        print("k <number>: Keep file number <number> and delete the rest")
        print("s: Skip this set (do nothing)")
        print("a: Skip all remaining sets")

        action = input("Your choice: ").strip().lower()
        parts = action.split()

        if parts[0] == 's':
            return ('skip', None)
        if parts[0] == 'a':
            return ('skip_all', None)

        if len(parts) == 2 and parts[1].isdigit():
            num = int(parts[1])
            if 1 <= num <= len(file_set):
                if parts[0] == 'k':
                    return ('keep_one', num - 1)

        print("Invalid input. Please try again. (e.g., 'k 1' to keep the first file)")
