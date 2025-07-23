import subprocess
import os
from pathlib import Path
from .helper import Status
from .plugins.cmd_decrypt import cli, FFMeta, FfmpegFileDecrypter

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

    def convert(self):
        subprocess.run(["audible", "decrypt", "-a", "-r","-f", "-c", "-d", 
             self.audiobook_download_directory.resolve()], cwd=self.audiobook_download_directory.resolve())
        if(len(get_m4b_audiobooks_in_directory(self.audiobook_download_directory.resolve()))):
            return Status.CONVERTED
        else:
            if(len(get_aax_audiobooks_in_directory(self.audiobook_download_directory.resolve())) == 0):
                return Status.NOT_DOWNLOADED
            else:
                return Status.ERROR
    
    def set_metadata(self):
        # supported tags
        # https://blog.travisflix.com/supported-mp4-metadata-keys-with-ffmpeg/
        # add pure path
        # https://docs.python.org/3/library/pathlib.html
        metadata = [
            ["artist", self.authors],
            ["album", self.title],
            ["publisher", self.publisher],
            ["year", self.publishing_date],
            ["composer", self.narrators],
            ["description", self.description],
            ["genre", self.genres],
            ["language", self.language],
            ["asin", self.asin]
        ]
        if self.subtitle is not None:
            metadata.append(["subtitle", self.subtitle])
        if self.series_name is not None:
            metadata.append(["series", self.series_name])
        if self.series_sequence is not None:
            metadata.append(["series-part", self.series_sequence])
        base_cmd = [
            "ffmpeg",
            "-v",
            "quiet",
        ]
        converted_audiobooks = get_m4b_audiobooks_in_directory(self.audiobook_download_directory)
        if len(converted_audiobooks) == 1:
            base_cmd.extend(
                [
                    "-i",
                    str((self.audiobook_download_directory / converted_audiobooks[0]).resolve()),
                ]
            )
        else:
            print("TODO fix multiple files for audiobook")
            exit
        # allows custom metadata tags
        base_cmd.extend(
            [
                "-movflags",
                "+use_metadata_tags",
            ]
        )
        # for each
        for tag in metadata:
            base_cmd.extend(
                [
                    "-metadata",
                    str(tag[0]) + "=" + str(tag[1]),
                ]
            )
        base_cmd.extend(
            [
                "-c",
                "copy",
            ]
        )
        if len(converted_audiobooks) == 1:
            base_cmd.extend([str((self.audiobook_download_directory / str("converted" + converted_audiobooks[0])).resolve())])
        else:
            print("TODO fix multiple files for audiobook")
            exit
        base_cmd.extend(["-y"])
        print(base_cmd)
        subprocess.run(base_cmd)
        # converted_audiobooks = get_m4b_audiobooks_in_directory(self.audiobook_download_directory)
        # if len(converted_audiobooks) != 1:
        #     exit
        # audiobook_path = self.audiobook_download_directory + "/" + converted_audiobooks[0]
        # print(audiobook_path)