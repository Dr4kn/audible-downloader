import subprocess
import os
from pathlib import Path
from .book import Book
from .helper import Status
from .plugins.cmd_decrypt import cli, FFMeta, FfmpegFileDecrypter

def get_aax_audiobooks_in_directory(audiobook_download_directory):
    return [each for each in os.listdir(audiobook_download_directory) if each.endswith(('.aax', '.aaxc'))]

def get_m4b_audiobooks_in_directory(audiobook_download_directory):
    return [each for each in os.listdir(audiobook_download_directory) if each.endswith(('.m4b'))]
class Downloader:
    def __init__(self, download_path: os.path, book: Book):
        self.download_path = download_path
        self.asin = book.asin
        self.book = book
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
    
    def set_metadata(self):
        # supported tags
        # https://blog.travisflix.com/supported-mp4-metadata-keys-with-ffmpeg/
        # add pure path
        # https://docs.python.org/3/library/pathlib.html
        metadata = [
            ["artist", self.book.authors],
            ["album", self.book.title],
            ["publisher", self.book.publisher],
            ["year", self.book.publishing_date],
            ["composer", self.book.narrators],
            ["description", self.book.description],
            ["genre", self.book.genres],
            ["language", self.book.language],
            ["asin", self.book.asin]
        ]
        if self.book.subtitle is not None:
            metadata.append(["subtitle", self.book.subtitle])
        if self.book.series_name is not None:
            metadata.append(["series", self.book.series_name])
        if self.book.series_sequence is not None:
            metadata.append(["series-part", self.book.series_sequence])
        base_cmd = [
            "ffmpeg",
            "-v",
            "quiet",
        ]
        converted_audiobooks = get_m4b_audiobooks_in_directory(self.audiobook_download_directory)
        if len(converted_audiobooks) == 1:
            base_cmd.extend(
                [
                    "i",
                    self.audiobook_download_directory + "/" + converted_audiobooks[0],
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
            base_cmd.extend([self.audiobook_download_directory + "/converted" + converted_audiobooks[0]])
        else:
            print("TODO fix multiple files for audiobook")
            exit
        base_cmd.extend(["-y"])
        print(base_cmd)
        exit
        # converted_audiobooks = get_m4b_audiobooks_in_directory(self.audiobook_download_directory)
        # if len(converted_audiobooks) != 1:
        #     exit
        # audiobook_path = self.audiobook_download_directory + "/" + converted_audiobooks[0]
        # print(audiobook_path)