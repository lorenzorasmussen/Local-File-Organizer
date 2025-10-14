import os
import time
import config
from file_utils import (
    display_directory_tree,
    collect_file_paths,
)
from data_processing_common import (
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
from output_filter import filter_specific_output
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from ui import get_yes_no, get_mode_selection, get_paths, print_simulated_tree, get_main_menu_selection, get_ai_backend_selection
from organize_files import organize_files_with_ai
from ollama import Client
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def ensure_nltk_data():
    """Ensure that NLTK data is downloaded efficiently and quietly."""
    import nltk
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)

# Initialize models
image_inference = None
text_inference = None

def initialize_local_models():
    """Initialize the local GGUF models if they haven't been initialized yet."""
    global image_inference, text_inference

    if image_inference is None or text_inference is None:
        model_path = "llava-v1.6-vicuna-7b:q4_0"
        model_path_text = "Llama3.2-3B-Instruct:q3_K_M"

        base_model_name = model_path.split(':')[0]
        model_path_llava_mmproj = f"{base_model_name}-mmproj.gguf"

        with filter_specific_output():
            chat_handler_llava = Llava15ChatHandler(clip_model_path=model_path_llava_mmproj, verbose=True)
            image_inference = Llama(
                model_path=model_path,
                chat_handler=chat_handler_llava,
                n_ctx=2048,
                n_gpu_layers=0,
                verbose=True
            )
            text_inference = Llama(
                model_path=model_path_text,
                n_ctx=2048,
                n_gpu_layers=0,
                verbose=True
            )
        print("**----------------------------------------------**")
        print("**       Image inference model initialized      **")
        print("**       Text inference model initialized       **")
        print("**----------------------------------------------**")
    return {'image': image_inference, 'text': text_inference}

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
def one_time_organization(silent_mode, log_file):
    """Handle one-time file organization."""
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

    if not silent_mode:
        print("-" * 50)
        print("Directory tree before organizing:")
        display_directory_tree(input_path)
        print("*" * 50)

    while True:
        mode = get_mode_selection()
        if mode == config.CONTENT_MODE:
            ai_backend = get_ai_backend_selection()
            client_or_model = None
            model_name = None
            if ai_backend == 'Ollama':
                client_or_model = Client(host='http://localhost:11434')
                model_name = 'moondream'
            else:
                if not silent_mode:
                    print("Checking if the model is already downloaded. If not, downloading it now.")
                client_or_model = initialize_local_models()

            if not silent_mode:
                print("*" * 50)
                print("The file upload was successful. Processing may take a few minutes.")
                print("*" * 50)

            operations = organize_files_with_ai(
                file_paths,
                output_path,
                ai_backend,
                client_or_model,
                model_name,
                silent_mode,
                log_file
            )
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

class WatcherEventHandler(FileSystemEventHandler):
    def __init__(self, output_path, mode, silent_mode, log_file, ai_backend=None, client_or_model=None, model_name=None):
        self.output_path = output_path
        self.mode = mode
        self.silent_mode = silent_mode
        self.log_file = log_file
        self.ai_backend = ai_backend
        self.client_or_model = client_or_model
        self.model_name = model_name

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            file_path = [event.src_path]
            operations = []
            if self.mode == config.CONTENT_MODE:
                operations = organize_files_with_ai(
                    file_path,
                    self.output_path,
                    self.ai_backend,
                    self.client_or_model,
                    self.model_name,
                    self.silent_mode,
                    self.log_file
                )
            elif self.mode == config.DATE_MODE:
                operations = process_files_by_date(file_path, self.output_path, dry_run=False, silent=self.silent_mode, log_file=self.log_file)
            elif self.mode == config.TYPE_MODE:
                operations = process_files_by_type(file_path, self.output_path, dry_run=False, silent=self.silent_mode, log_file=self.log_file)

            execute_operations(operations, dry_run=False, silent=self.silent_mode, log_file=self.log_file)
            print(f"Organized {event.src_path}")

def start_watching(input_path, output_path, mode, silent_mode, log_file, ai_backend=None, client_or_model=None, model_name=None):
    """Start watching a directory for new files."""
    event_handler = WatcherEventHandler(output_path, mode, silent_mode, log_file, ai_backend, client_or_model, model_name)
    observer = Observer()
    observer.schedule(event_handler, input_path, recursive=True)
    observer.start()
    print(f"Watching directory: {input_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    ensure_nltk_data()
    print("-" * 50)
    print("**NOTE: Silent mode logs all outputs to a text file instead of displaying them in the terminal.")
    silent_mode = get_yes_no("Would you like to enable silent mode? (yes/no): ")
    log_file = config.LOG_FILE if silent_mode else None

    while True:
        main_menu_selection = get_main_menu_selection()
        if main_menu_selection == 'one-time':
            one_time_organization(silent_mode, log_file)
            another_directory = get_yes_no("Would you like to organize another directory? (yes/no): ")
            if not another_directory:
                break
        elif main_menu_selection == 'watch':
            input_path, output_path = get_paths( silent_mode, log_file)
            mode = get_mode_selection()

            ai_backend = None
            client_or_model = None
            model_name = None

            if mode == config.CONTENT_MODE:
                ai_backend = get_ai_backend_selection()
                if ai_backend == 'Ollama':
                    client_or_model = Client(host='http://localhost:11434')
                    model_name = 'moondream'
                else:
                    client_or_model = initialize_local_models()

            start_watching(input_path, output_path, mode, silent_mode, log_file, ai_backend, client_or_model, model_name)
            break
        elif main_menu_selection == 'exit':
            break

if __name__ == '__main__':
    main()