"""
Configuration module for the audiobook downloader.
Contains all configuration constants and environment settings.
"""

import os
import sys

# Ensure stdout is flushed immediately for Docker logging
sys.stdout.reconfigure(line_buffering=True)

# Directory configuration
CONFIG_DIR = "/config"
AUDIOBOOK_DOWNLOAD_DIR = "/app"
AUDIOBOOK_DIR = "/audiobooks"

# Environment settings
USE_FOLDERS = True if os.getenv('AUDIOBOOK_FOLDERS') == "True" else False

# Database configuration
DATABASE_PATH = os.path.join(CONFIG_DIR, "audiobooks.db")

# Audible CLI configuration
AUDIBLE_TIMEOUT = "0"  # No timeout for downloads
DOWNLOAD_QUALITY = "best"
FILENAME_MODE = "asin_ascii"

# Batch processing settings
API_BATCH_SIZE = 20  # Number of books to check in one API call