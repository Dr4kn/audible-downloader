import os
import subprocess
import time
class Downloader:
    def __init__(self, download_path: os.path, asin: str):
        self.download_path = download_path
        self.asin = asin
        self.audiobook_download_directory = self.download_path + self.asin

    def download(self):
        os.makedirs(self.audiobook_download_directory, exist_ok=True)

        subprocess.run(
            ["audible", "download", "-a", self.asin, 
            "--aax-fallback", "--timeout", "0", 
            "-f", "asin_ascii", "--ignore-podcasts", 
            "-o", self.audiobook_download_directory, 
            "--chapter", "--pdf", "--cover"])

    def convert(self):
        subprocess.run(["audible", "decrypt", "-a", "-r","-f", "-c", "-d", self.audiobook_download_directory], cwd=audiobook_download_directory)