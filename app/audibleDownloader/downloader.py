import os
import subprocess
from .helper import Status

def get_aax_audiobooks_in_directory(audiobook_download_directory):
    return [each for each in os.listdir(audiobook_download_directory) if each.endswith(('.aax', '.aaxc'))]

def get_m4b_audiobooks_in_directory(audiobook_download_directory):
    return [each for each in os.listdir(audiobook_download_directory) if each.endswith(('.m4b'))]
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
        if(len(get_aax_audiobooks_in_directory(self.audiobook_download_directory))):
            return Status.DOWNLOADED
        else:
            return Status.ERROR

    def convert(self):
        subprocess.run(["audible", "decrypt", "-a", "-r","-f", "-c", "-d", 
             self.audiobook_download_directory], cwd=self.audiobook_download_directory)
        if(len(get_m4b_audiobooks_in_directory(self.audiobook_download_directory))):
            return Status.CONVERTED
        else:
            if(len(get_aax_audiobooks_in_directory(self.audiobook_download_directory)) == 0):
                return Status.NOT_DOWNLOADED
            else:
                return Status.ERROR