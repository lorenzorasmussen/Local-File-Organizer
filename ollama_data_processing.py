import ollama
import base64
from tqdm import tqdm
from file_utils import get_new_filename

def process_text_files_ollama(text_tuples, silent=False, log_file=None):
    """
    Processes text files using Ollama for summarization and categorization.
    """
    data_texts = []
    if not silent:
        print("Processing text files with Ollama...")
    for file_path, text_content in tqdm(text_tuples, desc="Processing text files", disable=silent):
        try:
            response = ollama.chat(
                model='llama3',
                messages=[
                    {
                        'role': 'user',
                        'content': f"Summarize the following text and suggest a file category and a new filename: {text_content}",
                    },
                ],
            )
            summary = response['message']['content']
            category, new_filename = get_new_filename(summary, file_path)
            data_texts.append({
                "file_path": file_path,
                "category": category,
                "new_filename": new_filename,
                "summary": summary
            })
        except Exception as e:
            message = f"Error processing {file_path} with Ollama: {e}"
            if silent and log_file:
                with open(log_file, 'a') as f:
                    f.write(message + '\n')
            else:
                print(message)
    return data_texts

def process_image_files_ollama(image_files, silent=False, log_file=None):
    """
    Processes image files using Ollama for summarization and categorization.
    """
    data_images = []
    if not silent:
        print("Processing image files with Ollama...")
    for file_path in tqdm(image_files, desc="Processing image files", disable=silent):
        try:
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            response = ollama.chat(
                model='llava',
                messages=[
                    {
                        'role': 'user',
                        'content': 'Describe this image and suggest a category and a new filename.',
                        'images': [image_data]
                    }
                ]
            )
            summary = response['message']['content']
            category, new_filename = get_new_filename(summary, file_path)
            data_images.append({
                "file_path": file_path,
                "category": category,
                "new_filename": new_filename,
                "summary": summary
            })
        except Exception as e:
            message = f"Error processing {file_path} with Ollama: {e}"
            if silent and log_file:
                with open(log_file, 'a') as f:
                    f.write(message + '\n')
            else:
                print(message)
    return data_images