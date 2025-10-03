"""
Audiobook Downloader Package
A modular audiobook downloading and management system.
"""

from .main import main, AudiobookDownloaderApp
from .library_manager import library_manager
from .restriction_checker import restriction_checker
from .integrity_checker import integrity_checker
from .downloader import downloader
from .file_processor import file_processor
from .audible_api import audible_api
from .database import db
from . import config

__version__ = "2.0.0"
__author__ = "Audiobook Downloader Contributors"

__all__ = [
    'main',
    'AudiobookDownloaderApp',
    'library_manager',
    'restriction_checker', 
    'integrity_checker',
    'downloader',
    'file_processor',
    'audible_api',
    'db',
    'config'
]