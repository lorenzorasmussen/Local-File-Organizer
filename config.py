"""
Configuration settings for the file organizer.
"""

# Model paths
IMAGE_MODEL_PATH = "llava-v1.6-vicuna-7b:q4_0"
TEXT_MODEL_PATH = "Llama3.2-3B-Instruct:q3_K_M"

# Model parameters
DEFAULT_TEMPERATURE = 0.3
MAX_NEW_TOKENS = 3000
TOP_K = 3
TOP_P = 0.2

# File organizing modes
CONTENT_MODE = 'content'
DATE_MODE = 'date'
TYPE_MODE = 'type'

# Logging
LOG_FILE = 'operation_log.txt'
SILENT_MODE = False
