import os
import time
import config
from file_utils import (
    display_directory_tree,
    collect_file_paths,
    separate_files_by_type,
    read_file_data
)
from data_processing_common import (
    compute_operations,
    execute_operations,
    process_files_by_date,
    process_files_by_type,
)
from text_data_processing import process_text_files
from image_data_processing import process_image_files
from ollama_data_processing import process_text_files_ollama, process_image_files_ollama
from output_filter import filter_specific_output
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from ui import (
    get_yes_no, get_mode_selection, get_paths, print_simulated_tree,
    get_backend_selection, get_main_menu_selection, display_duplicates,
    get_duplicate_handling_choice, get_individual_duplicate_action
)
from watch_mode import start_watching
from duplicate_finder import find_duplicates
from duplicate_handler import (
    handle_duplicates_delete_all, handle_duplicates_move_all,
    handle_individual_duplicate
)

def ensure_nltk_data():
    """Ensure that NLTK data is downloaded efficiently and quietly."""
    import nltk
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)

# Initialize models
image_inference = None
text_inference = None

def initialize_models():
    """Initialize the models if they haven't been initialized yet."""
    global image_inference, text_inference

    if image_inference is None or text_inference is None:
        model_path = "llava-v1.6-vicuna-7b:q4_0"
        model_path_text = "Llama3.2-3B-Instruct:q3_K_M"

        # For LLaVA model (image_inference)
        # Assumes mmproj file is named by appending "-mmproj.gguf" to the main model name
        # e.g. if model_path is "llava-v1.6-vicuna-7b:q4_0", mmproj is "llava-v1.6-vicuna-7b-mmproj.gguf"
        # The :q4_0 part is a quantization indicator and should be removed for the mmproj filename.
        base_model_name = model_path.split(':')[0] # Get "llava-v1.6-vicuna-7b"
        model_path_llava_mmproj = f"{base_model_name}-mmproj.gguf"

        # Use the filter_specific_output context manager
        with filter_specific_output():
            # Initialize the LLaVA chat handler
            chat_handler_llava = Llava15ChatHandler(clip_model_path=model_path_llava_mmproj, verbose=True)

            # Initialize the image inference model (LLaVA)
            image_inference = Llama(
                model_path=model_path,  # This is the main LLaVA model GGUF
                chat_handler=chat_handler_llava,
                n_ctx=2048,  # Default context size, can be adjusted
                n_gpu_layers=0, # Ensure CPU usage
                verbose=True # For debugging
            )

            # Initialize the text inference model
            text_inference = Llama(
                model_path=model_path_text,
                n_ctx=2048,  # Default context size
                n_gpu_layers=0, # Ensure CPU usage
                verbose=True # For debugging
            )
        print("**----------------------------------------------**")
        print("**       Image inference model initialized      **")
        print("**       Text inference model initialized       **")
        print("**----------------------------------------------**")

def simulate_directory_tree(operations, base_path):
    """Simulate the directory tree based on the proposed operations."""
    tree = {}
    for op in operations:
        rel_path = os.path.relpath(op['destination'], base_path)
        parts = rel_path.split(os.sep)
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
    return tree

def organize_directory_once(silent_mode, log_file):
    """Handles the one-time organization of a directory."""
    input_path, output_path = get_paths(silent_mode, log_file)
    start_time = time.time()
    file_paths = collect_file_paths(input_path)
    end_time = time.time()
    message = f"Time taken to load file paths: {end_time - start_time:.2f} seconds"
    if silent_mode:
        with open(log_file, 'a') as f:
            f.write(message + '\n')
    else:
        print(message)

    if not silent_mode:
        print("-" * 50)
        print("Directory tree before organizing:")
        display_directory_tree(input_path)
        print("*" * 50)

    while True:
        mode = get_mode_selection()
        if mode == config.CONTENT_MODE:
            backend = get_backend_selection()
            if backend == 'local':
                if not silent_mode:
                    print("Checking if the model is already downloaded. If not, downloading it now.")
                initialize_models()
                if not silent_mode:
                    print("*" * 50)
                    print("The file upload was successful. Processing may take a few minutes.")
                    print("*" * 50)
                image_files, text_files = separate_files_by_type(file_paths)
                text_tuples = []
                for fp in text_files:
                    text_content = read_file_data(fp)
                    if text_content is None:
                        message = f"Unsupported or unreadable text file format: {fp}"
                        if silent_mode:
                            with open(log_file, 'a') as f:
                                f.write(message + '\n')
                        else:
                            print(message)
                        continue
                    text_tuples.append((fp, text_content))
                data_images = process_image_files(image_files, image_inference, text_inference, silent=silent_mode, log_file=log_file)
                data_texts = process_text_files(text_tuples, text_inference, silent=silent_mode, log_file=log_file)

            elif backend == 'ollama':
                image_files, text_files = separate_files_by_type(file_paths)
                text_tuples = []
                for fp in text_files:
                    text_content = read_file_data(fp)
                    if text_content is None:
                        message = f"Unsupported or unreadable text file format: {fp}"
                        if silent_mode:
                            with open(log_file, 'a') as f:
                                f.write(message + '\n')
                        else:
                            print(message)
                        continue
                    text_tuples.append((fp, text_content))
                data_images = process_image_files_ollama(image_files, silent=silent_mode, log_file=log_file)
                data_texts = process_text_files_ollama(text_tuples, silent=silent_mode, log_file=log_file)
            all_data = data_images + data_texts
            operations = compute_operations(all_data, output_path, set(), set())
        elif mode == config.DATE_MODE:
            operations = process_files_by_date(file_paths, output_path, dry_run=False, silent=silent_mode, log_file=log_file)
        elif mode == config.TYPE_MODE:
            operations = process_files_by_type(file_paths, output_path, dry_run=False, silent=silent_mode, log_file=log_file)
        else:
            print("Invalid mode selected.")
            return

        print("-" * 50)
        message = "Proposed directory structure:"
        if silent_mode:
            with open(log_file, 'a') as f:
                f.write(message + '\n')
        else:
            print(message)
            print(os.path.abspath(output_path))
            simulated_tree = simulate_directory_tree(operations, output_path)
            print_simulated_tree(simulated_tree)
            print("-" * 50)

        proceed = get_yes_no("Would you like to proceed with these changes? (yes/no): ")
        if proceed:
            os.makedirs(output_path, exist_ok=True)
            message = "Performing file operations..."
            if silent_mode:
                with open(log_file, 'a') as f:
                    f.write(message + '\n')
            else:
                print(message)
            execute_operations(operations, dry_run=False, silent=silent_mode, log_file=log_file)
            message = "The files have been organized successfully."
            if silent_mode:
                with open(log_file, 'a') as f:
                    f.write("-" * 50 + '\n' + message + '\n' + "-" * 50 + '\n')
            else:
                print("-" * 50)
                print(message)
                print("-" * 50)
            break
        else:
            another_sort = get_yes_no("Would you like to choose another sorting method? (yes/no): ")
            if not another_sort:
                print("Operation canceled by the user.")
                break

def handle_duplicates_workflow(silent_mode, log_file):
    """Handles the workflow for finding and managing duplicate files."""
    if not silent_mode:
        print("\n" + "="*50)
        print(" " * 10 + "Find and Handle Duplicate Files")
        print("="*50)

    # For finding duplicates, we only need an input path.
    # We can reuse get_paths and just ignore the output_path.
    input_path, _ = get_paths(silent_mode, log_file)

    duplicate_sets = find_duplicates(input_path)
    display_duplicates(duplicate_sets)

    if not duplicate_sets:
        return

    choice = get_duplicate_handling_choice()

    if choice == 'delete_all':
        handle_duplicates_delete_all(duplicate_sets, silent_mode, log_file)
        print("\nDuplicate deletion process completed.")

    elif choice == 'move_all':
        move_to_folder = os.path.join(input_path, "duplicates")
        handle_duplicates_move_all(duplicate_sets, move_to_folder, silent_mode, log_file)
        print(f"\nDuplicates moved to {move_to_folder}.")

    elif choice == 'decide_each':
        for file_set in duplicate_sets:
            action, index_to_keep = get_individual_duplicate_action(file_set)
            if action == 'skip':
                continue
            if action == 'skip_all':
                print("Skipping all remaining sets.")
                break
            if action == 'keep_one':
                handle_individual_duplicate(file_set, action, index_to_keep, silent_mode, log_file)
        print("\nIndividual duplicate handling completed.")

    elif choice == 'skip':
        print("\nSkipping duplicate handling.")

def main():
    ensure_nltk_data()
    print("-" * 50)
    print("**NOTE: Silent mode logs all outputs to a text file instead of displaying them in the terminal.")
    silent_mode = get_yes_no("Would you like to enable silent mode? (yes/no): ")
    log_file = config.LOG_FILE if silent_mode else None

    while True:
        main_choice = get_main_menu_selection()

        if main_choice == 'organize':
            organize_directory_once(silent_mode, log_file)

        elif main_choice == 'watch':
            input_path, output_path = get_paths(silent_mode, log_file)
            backend = get_backend_selection()
            models = (None, None)
            if backend == 'local':
                if not silent_mode:
                    print("Initializing local models for watch mode...")
                initialize_models()
                models = (image_inference, text_inference)

            start_watching(input_path, output_path, backend, models, silent_mode, log_file)

        elif main_choice == 'duplicates':
            handle_duplicates_workflow(silent_mode, log_file)

        elif main_choice == 'exit':
            print("Exiting program.")
            break

if __name__ == '__main__':
    main()
