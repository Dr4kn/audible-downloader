from pathlib import Path
from .book import Book
import subprocess

class Decyrpter:
    def __init__(self, book: Book, activation_bytes: str, remove_intro_outro = True):
        print(book.asin)
        self.book = book
        self.activation_bytes = activation_bytes
        self.aax_books = []
        self.cover, self.pdf, self.chapters, self.voucher = None, None, None, None
        # TODO remove after testing
        self.metadata = None 
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
                # TODO remove after testing
                case ".meta":
                    self.metadata = file

    @property
    def base_cmd(self) -> list[str]:
        base_cmd = [
            "ffmpeg",
            # "-v",
            # "quiet",
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
        base_cmd.extend([
            "-i",
            str(self.metadata),
        ])
        base_cmd.extend([
            "-i",
            str(self.cover),
        ])
        set_cover = [
            "-map", # use only the audio of the audiobook
            "0:a",
            "-map", # set the cover and metadata
            "2:v",
            "-disposition:v:0", # treat video stream as attached picture
            "attached_pic",
            "-metadata:s:v",
            "title=Album cover",
            "-metadata:s:v",
            "comment=Cover (Front)",
        ]
        base_cmd.extend(set_cover)
        set_metadata = [
            "-map_metadata",
            "1",
            "-map_metadata", # copy metadata in the original that isn't in the metadata file to the output
            "0",
            "-metadata",
            "genre=fantasy",
            "-metadata",
            "description=how, asdfasd, sadfsadfsdafsdf",
            "-metadata",
            "asin=187",
        ]
        base_cmd.extend(set_metadata)
        faststart = [ # can slighlty improve playback performance when streaming.
            "-movflags", 
            "+faststart",
        ]
        base_cmd.extend(faststart)

        outputfile = [
            "-c",
            "copy",
            str(self.aax_books[0].with_suffix(".m4b"))
        ]
        base_cmd.extend(outputfile)
        print(base_cmd)
        subprocess.run(base_cmd)
        print("fin")

        
