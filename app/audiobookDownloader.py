#!/usr/bin/env python3
"""
Audiobook Downloader Entry Point
Simple entry point that imports and runs the modular application.
"""

from main import AudiobookDownloaderApp

if __name__ == "__main__":
    app = AudiobookDownloaderApp()
    app.run()