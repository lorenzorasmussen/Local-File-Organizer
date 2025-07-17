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
from output_filter import filter_specific_output
from nexa.gguf import NexaVLMInference, NexaTextInference
from ui import get_yes_no, get_mode_selection, get_paths, print_simulated_tree

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
        with filter_specific_output():
            image_inference = NexaVLMInference(
                model_path=config.IMAGE_MODEL_PATH,
                local_path=None,
                stop_words=[],
                temperature=config.DEFAULT_TEMPERATURE,
                max_new_tokens=config.MAX_NEW_TOKENS,
                top_k=config.TOP_K,
                top_p=config.TOP_P,
                profiling=False
            )
            text_inference = NexaTextInference(
                model_path=config.TEXT_MODEL_PATH,
                local_path=None,
                stop_words=[],
                temperature=0.5,
                max_new_tokens=config.MAX_NEW_TOKENS,
                top_k=config.TOP_K,
                top_p=0.3,
                profiling=False
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

def main():
    ensure_nltk_data()
    dry_run = True
    print("-" * 50)
    print("**NOTE: Silent mode logs all outputs to a text file instead of displaying them in the terminal.")
    silent_mode = get_yes_no("Would you like to enable silent mode? (yes/no): ")
    log_file = config.LOG_FILE if silent_mode else None

    while True:
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
        another_directory = get_yes_no("Would you like to organize another directory? (yes/no): ")
        if not another_directory:
            break

if __name__ == '__main__':
    main()
