import subprocess
import os
from pathlib import Path
from .helper import Status

def get_aax_audiobooks_in_directory(audiobook_download_directory: Path):
    return [each for each in os.listdir(audiobook_download_directory.resolve()) if each.endswith(('.aax', '.aaxc'))]

def get_m4b_audiobooks_in_directory(audiobook_download_directory: Path):
    return [each for each in os.listdir(audiobook_download_directory.resolve()) if each.endswith(('.m4b'))]

class Book:
    def __init__(self, book: list, download_path=os.path.expanduser("~/.config/audible/")):
        self.asin = book[0]
        self.authors = book[1]
        self.title = book[2]
        self.subtitle = book[3]
        self.series_name = book[4]
        self.series_sequence = book[5]
        self.description = book[6]
        self.narrators = book[7]
        self.language = book[8]
        self.publisher = book[9]
        self.publishing_date = book[10]
        self.genres = book[11]
        self.content_delivery_type = book[12]
        self.purchase_date = book[13]
        self.product_image = book[14]
        self.pdf_url = book[15]
        if book[16] == 0:
            self.status = Status.NOT_DOWNLOADED
        elif book[17] == 0:
            self.status = Status.DOWNLOADED
        elif book[18] == 0:
            self.status = Status.CONVERTED
        elif book[18] == 1:
            self.status = Status.MOVED
        else:
            self.status = Status.ERROR
        if type(download_path) is not Path:
            self.download_path = Path(download_path)
        else:
            self.download_path
        self.audiobook_download_directory = (self.download_path / self.asin)
    
    def set_path(self, download_path: Path):
        self.download_path = download_path
        self.audiobook_download_directory = download_path / self.asin

    def download(self):
        os.makedirs(self.audiobook_download_directory.resolve(), exist_ok=True)

        subprocess.run(
            ["audible", "download", "-a", self.asin, 
            "--aax-fallback", "--timeout", "0", 
            "-f", "asin_ascii", "--ignore-podcasts", 
            "-o", self.audiobook_download_directory.resolve(), 
            "--chapter", "--pdf", "--cover"])
        if(len(get_aax_audiobooks_in_directory(self.audiobook_download_directory.resolve()))):
            return Status.DOWNLOADED
        else:
            return Status.ERROR
