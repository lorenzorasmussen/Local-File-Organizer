# Local File Organizer: AI File Management Run Entirely on Your Device, Privacy Assured

Tired of digital clutter? Overwhelmed by disorganized files scattered across your computer? Let AI do the heavy lifting! The Local File Organizer is your personal organizing assistant, using cutting-edge AI to bring order to your file chaos - all while respecting your privacy.

## How It Works 💡

Before:

```
/home/user/messy_documents/
├── IMG_20230515_140322.jpg
├── IMG_20230516_083045.jpg
├── IMG_20230517_192130.jpg
├── budget_2023.xlsx
├── meeting_notes_05152023.txt
├── project_proposal_draft.docx
├── random_thoughts.txt
├── recipe_chocolate_cake.pdf
├── scan0001.pdf
├── vacation_itinerary.docx
└── work_presentation.pptx

0 directories, 11 files
```

After:

```
/home/user/organized_documents/
├── Financial
│   └── 2023_Budget_Spreadsheet.xlsx
├── Food_and_Recipes
│   └── Chocolate_Cake_Recipe.pdf
├── Meetings_and_Notes
│   └── Team_Meeting_Notes_May_15_2023.txt
├── Personal
│   └── Random_Thoughts_and_Ideas.txt
├── Photos
│   ├── Cityscape_Sunset_May_17_2023.jpg
│   ├── Morning_Coffee_Shop_May_16_2023.jpg
│   └── Office_Team_Lunch_May_15_2023.jpg
├── Travel
│   └── Summer_Vacation_Itinerary_2023.docx
└── Work
    ├── Project_X_Proposal_Draft.docx
    ├── Quarterly_Sales_Report.pdf
    └── Marketing_Strategy_Presentation.pptx

7 directories, 11 files
```

## Updates 🚀

**[2024/09] v0.0.2**:
* Dry Run Mode: check sorting results before committing changes
* Silent Mode: save all logs to a txt file for quieter operation
* Added file support:  `.md`, .`excel`, `.ppt`, and `.csv` 
* Three sorting options: by content, by date, and by type
* The default text model is a GGUF version of Llama 3.2 3B (or similar).
* Improved CLI interaction experience
* Added real-time progress bar for file analysis

Please update the project by deleting the original project folder and reinstalling the requirements. Refer to the installation guide from Step 4.


## Roadmap 📅

- [ ] Copilot Mode: chat with AI to tell AI how you want to sort the file (ie. read and rename all the PDFs)
- [ ] Change models with CLI 
- [ ] ebook format support
- [ ] audio file support
- [ ] video file support
- [ ] Implement best practices like Johnny Decimal
- [ ] Check file duplication
- [ ] Dockerfile for easier installation
- [ ] People from [Nexa](https://github.com/NexaAI/nexa-sdk) is helping me to make executables for macOS, Linux and Windows

## What It Does 🔍

This intelligent file organizer harnesses the power of advanced AI models, including language models (LMs) and vision-language models (VLMs), to automate the process of organizing files by:


* Scanning a specified input directory for files.
* Content Understanding: 
  - **Textual Analysis**: Uses GGUF-formatted language models (e.g., Llama 3.2) loaded via `llama-cpp-python` to analyze and summarize text-based content, generating relevant descriptions and filenames.
  - **Visual Content Analysis**: Uses GGUF-formatted vision-language models (e.g., LLaVA 1.5/1.6) loaded via `llama-cpp-python` to interpret visual files such as images, providing context-aware categorization and descriptions.

* Understanding the content of your files (text, images, and more) to generate relevant descriptions, folder names, and filenames.
* Organizing the files into a new directory structure based on the generated metadata.

The best part? All AI processing happens 100% on your local device using `llama-cpp-python`. No internet connection required, no data leaves your computer, and no AI API is needed - keeping your files completely private and secure.


## Supported File Types 📁

- **Images:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`
- **Text Files:** `.txt`, `.docx`, `.md`
- **Spreadsheets:** `.xlsx`, `.csv`
- **Presentations:** `.ppt`, `.pptx`
- **PDFs:** `.pdf`

## Prerequisites 💻

- **Operating System:** Compatible with Windows, macOS, and Linux.
- **Python Version:** Python 3.12
- **Conda:** Anaconda or Miniconda installed.
- **Git:** For cloning the repository (or you can download the code as a ZIP file).

## Installation 🛠

> For issues related to `llama-cpp-python` installation, please refer to the [official `llama-cpp-python` GitHub issues page](https://github.com/abetlen/llama-cpp-python/issues). For model-related questions or if you need to find GGUF models, Hugging Face is a great resource.

### 1. Install Python

Before installing the Local File Organizer, make sure you have Python installed on your system. We recommend using Python 3.12 or later.

You can download Python from [the official website]((https://www.python.org/downloads/)).

Follow the installation instructions for your operating system.

### 2. Clone the Repository

Clone this repository to your local machine using Git:

```zsh
git clone https://github.com/QiuYannnn/Local-File-Organizer.git
```

Or download the repository as a ZIP file and extract it to your desired location.

### 3. Set Up the Python Environment

Create a new Conda environment named `local_file_organizer` with Python 3.12:

```zsh
conda create --name local_file_organizer python=3.12
```

Activate the environment:

```zsh
conda activate local_file_organizer
```

### 4. Install Core LLM Engine (`llama-cpp-python`)

This project uses `llama-cpp-python` for local Large Language Model (LLM) inference.

**Recommended Installation (macOS Intel & some other platforms):**

For macOS Intel users and potentially other platforms, try installing `llama-cpp-python` using pre-compiled CPU wheels. This can help avoid local compilation and the need for CMake and a C++ compiler directly:
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

**Other Platforms / Source Installation:**

If the above command doesn't work or you are on a different platform (e.g., Linux, Windows, macOS Apple Silicon for GPU support), you might need to install `llama-cpp-python` from source or use other specific wheels. This typically requires CMake and a C++ compiler (e.g., Xcode Command Line Tools on macOS, `build-essential` on Linux).

For detailed installation instructions, including GPU support (Metal for macOS, CUDA for NVIDIA, ROCm for AMD), please refer to the [official `llama-cpp-python` documentation](https://llama-cpp-python.readthedocs.io/en/latest/installation/).

**Note on `cmake` in `requirements.txt`:** The `requirements.txt` file includes `cmake`. This is listed because `llama-cpp-python` often needs it for compilation if a binary wheel isn't available or suitable for your system. Installing `cmake` via pip (`pip install cmake`) can sometimes fulfill this dependency for the `llama-cpp-python` build process.

### 5. Install Dependencies

1. Ensure you are in the project directory:
   ```zsh
   cd path/to/Local-File-Organizer
   ```
   Replace `path/to/Local-File-Organizer` with the actual path where you cloned or extracted the project.

2. Install the required dependencies:
   ```zsh
   pip install -r requirements.txt
   ```

**Note:** After successfully setting up `llama-cpp-python` as described in Step 4, ensure all other dependencies are installed by running `pip install -r requirements.txt`. If you encounter issues with specific packages, you may need to consult their respective documentation for installation troubleshooting. The `requirements.txt` file includes `cmake` as it's often a build dependency for `llama-cpp-python`.

With the environment activated and dependencies installed, run the script using:

### 6. Running the Script🎉
```zsh
python main.py
```

## Notes

- **LLM Models:**
  - The script uses `llama-cpp-python` to load and run GGUF-formatted Large Language Models (LLMs) for text analysis (e.g., Llama 3.2) and vision-language tasks (e.g., LLaVA).
  - You will need to download GGUF model files separately.
  - Ensure the model paths in `main.py` (e.g., `model_path` and `model_path_text`, and `model_path_llava_mmproj`) are correctly set to point to your downloaded GGUF files. You can find many GGUF models on Hugging Face.

- **Dependencies:**
  - **pytesseract:** Requires Tesseract OCR installed on your system.
    - **macOS:** `brew install tesseract`
    - **Ubuntu/Linux:** `sudo apt-get install tesseract-ocr`
    - **Windows:** Download from [Tesseract OCR Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - **PyMuPDF (fitz):** Used for reading PDFs.

- **Processing Time:**
  - Processing may take time depending on the number and size of files.
  - The script uses multiprocessing to improve performance.

- **Customizing Prompts:**
  - You can adjust prompts in `data_processing.py` to change how metadata is generated.

## License

This project is dual-licensed under the MIT License and Apache 2.0 License. You may choose which license you prefer to use for this project.

- See the [MIT License](LICENSE-MIT) for more details.