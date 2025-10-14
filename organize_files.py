import os
import base64
from ollama import Client
from file_utils import read_file_data, separate_files_by_type
from data_processing_common import compute_operations
from text_data_processing import process_text_files
from image_data_processing import process_image_files

def get_classification_ollama_image(client, file_path, model_name):
    """Get classification from Ollama for a single image file."""
    if not os.path.exists(file_path):
        return "File does not exist."
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()

        encoded_image = base64.b64encode(image_data).decode('utf-8')

        response = client.generate(
            model=model_name,
            prompt="Suggest a concise, one or two-word folder name for the provided image.",
            images=[encoded_image],
            stream=False,
        )
        return response['response'].strip()
    except Exception as e:
        return f"Error processing file with Ollama: {e}"

def get_classification_ollama_text(client, file_path, model_name):
    """Get classification from Ollama for a single text file."""
    if not os.path.exists(file_path):
        return "File does not exist."
    try:
        text_content = read_file_data(file_path)
        if text_content is None:
            return "Unsupported or unreadable text file."

        response = client.generate(
            model=model_name,
            prompt=f"Suggest a concise, one or two-word folder name for a document titled '{os.path.basename(file_path)}' with the following content:\n\n{text_content}",
            stream=False,
        )
        return response['response'].strip()
    except Exception as e:
        return f"Error processing file with Ollama: {e}"

def organize_files_with_ai(file_paths, output_path, ai_backend, client_or_model, model_name, silent_mode, log_file):
    """
    Organize files using the selected AI backend.
    """
    all_data = []
    image_files, text_files = separate_files_by_type(file_paths)

    if ai_backend == 'Ollama':
        for file_path in image_files:
            classification = get_classification_ollama_image(client_or_model, file_path, model_name)
            all_data.append({'file_path': file_path, 'classification': classification})

        for file_path in text_files:
            classification = get_classification_ollama_text(client_or_model, file_path, model_name)
            all_data.append({'file_path': file_path, 'classification': classification})

    else:  # Local GGUF
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

        data_images = process_image_files(image_files, client_or_model['image'], client_or_model['text'], silent=silent_mode, log_file=log_file)
        data_texts = process_text_files(text_tuples, client_or_model['text'], silent=silent_mode, log_file=log_file)
        all_data = data_images + data_texts

    return compute_operations(all_data, output_path, set(), set())