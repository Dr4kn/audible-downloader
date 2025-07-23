from pathlib import Path
from .book import Book
import subprocess

class Decyrpter:
    def __init__(self, book: Book, activation_bytes: str, remove_intro_outro: True):
        print(book.asin)
        self.book = book
        self.activation_bytes = activation_bytes
        self.aax_books = []
        self.cover, self.pdf, self.chapters, self.voucher = None, None, None, None
        for file in list(self.book.audiobook_download_directory.iterdir()):
            match file.suffix:
                case ".aax":
                    self.aax_books.append(file)
                case ".jpg":
                    self.cover = file
                case ".pdf":
                    self.pdf = file
                case ".json":
                    self.chapters = file
                case ".voucher":
                    self.voucher = file

    @property
    def base_cmd(self) -> list[str]:
        base_cmd = [
            "ffmpeg",
            "-v",
            "quiet",
            "-y",
        ]
        if self.voucher is not None:
            print("aaxc isn't implemented yet")
            exit
        else:
            credentials_cmd = [
                "-activation_bytes",
                self.activation_bytes,
            ]
        base_cmd.extend(credentials_cmd)
        return base_cmd
    
    def decrypt(self):
        base_cmd = self.base_cmd
        # TODO check if aax or aaxc
        # TODO work with multiple audio files
        input_file = [
            "-i",
            str(self.aax_books[0]),
        ]
        base_cmd.extend(input_file)
        outputfile = [
            "-c",
            "copy",
            str(self.aax_books[0].with_suffix(".m4b"))
        ] 
        base_cmd.extend(outputfile)
        print(base_cmd)
        subprocess.run(base_cmd)
        print("fin")

        
