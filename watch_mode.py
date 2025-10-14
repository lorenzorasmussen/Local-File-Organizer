import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from file_utils import (
    separate_files_by_type,
    read_file_data
)
from data_processing_common import (
    compute_operations,
    execute_operations,
)
from text_data_processing import process_text_files
from image_data_processing import process_image_files
from ollama_data_processing import process_text_files_ollama, process_image_files_ollama

class FileOrganizerEventHandler(FileSystemEventHandler):
    def __init__(self, output_path, backend, models, silent=False, log_file=None):
        super().__init__()
        self.output_path = output_path
        self.backend = backend
        self.models = models
        self.silent = silent
        self.log_file = log_file

    def on_created(self, event):
        if not event.is_directory:
            # Wait a moment to ensure the file is fully written
            time.sleep(1)
            self.process_file(event.src_path)

    def process_file(self, file_path):
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return

        message = f"New file detected: {file_path}. Processing..."
        if self.silent:
            with open(self.log_file, 'a') as f:
                f.write(message + '\n')
        else:
            print(message)

        image_files, text_files = separate_files_by_type([file_path])
        all_data = []

        if self.backend == 'local':
            image_inference, text_inference = self.models
            if image_files:
                data_images = process_image_files(image_files, image_inference, text_inference, silent=self.silent, log_file=self.log_file)
                all_data.extend(data_images)
            if text_files:
                text_tuples = []
                for fp in text_files:
                    text_content = read_file_data(fp)
                    if text_content:
                        text_tuples.append((fp, text_content))
                data_texts = process_text_files(text_tuples, text_inference, silent=self.silent, log_file=self.log_file)
                all_data.extend(data_texts)

        elif self.backend == 'ollama':
            if image_files:
                data_images = process_image_files_ollama(image_files, silent=self.silent, log_file=self.log_file)
                all_data.extend(data_images)
            if text_files:
                text_tuples = []
                for fp in text_files:
                    text_content = read_file_data(fp)
                    if text_content:
                        text_tuples.append((fp, text_content))
                data_texts = process_text_files_ollama(text_tuples, silent=self.silent, log_file=self.log_file)
                all_data.extend(data_texts)

        if all_data:
            operations = compute_operations(all_data, self.output_path, set(), set())
            execute_operations(operations, dry_run=False, silent=self.silent, log_file=self.log_file)
            message = f"File {file_path} organized successfully."
            if self.silent:
                with open(self.log_file, 'a') as f:
                    f.write(message + '\n')
            else:
                print(message)
        else:
            message = f"Could not process file {file_path}. It might be an unsupported type or empty."
            if self.silent:
                with open(self.log_file, 'a') as f:
                    f.write(message + '\n')
            else:
                print(message)

def start_watching(input_path, output_path, backend, models, silent=False, log_file=None):
    event_handler = FileOrganizerEventHandler(output_path, backend, models, silent, log_file)
    observer = Observer()
    observer.schedule(event_handler, input_path, recursive=False)
    observer.start()
    message = f"Watching directory: {input_path}"
    if silent:
        with open(log_file, 'a') as f:
            f.write(message + '\n')
    else:
        print(message)
        print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        message = "\nWatcher stopped by user."
        if silent:
            with open(log_file, 'a') as f:
                f.write(message + '\n')
        else:
            print(message)
    observer.join()