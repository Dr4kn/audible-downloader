from pathlib import Path
from .book import Book
from .plugins.cmd_decrypt import FFMeta, ApiChapterInfo, _get_voucher_filename, _get_chapter_filename
import subprocess

class Decyrpter:
    def __init__(self, book: Book, activation_bytes: str, remove_intro_outro = True):
        print(book.asin)
        self.book = book
        self.activation_bytes = activation_bytes
        self.aax_books = []
        self.cover, self.pdf, self.chapters, self.voucher = None, None, None, None
        self.remove_intro_outro = remove_intro_outro
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

        # audible cmd_decyrpt
        self._api_chapter = None
        # TODO multiple input files
        self._source = self.aax_books[0]
        base_cmd = self.base_cmd
        self.book_path = self.aax_books[0]
        self.metafile = self.create_meta_file(base_cmd, self.book_path)
        self.ffmeta = FFMeta(self.metafile)

    @property
    def api_chapter(self) -> ApiChapterInfo:
        if self._api_chapter is None:
            try:
                voucher_filename = _get_voucher_filename(self._source)
                self._api_chapter = ApiChapterInfo.from_file(voucher_filename)
            except:
                voucher_filename = _get_chapter_filename(self._source)
                self._api_chapter = ApiChapterInfo.from_file(voucher_filename)
        return self._api_chapter

    @property
    def rebuild_chapters(self) -> None:
        # if not self._is_rebuilded:
        self.ffmeta.update_chapters_from_chapter_info(
            self.api_chapter, True, False, self.remove_intro_outro
        )
        # self._is_rebuilded = True

                   

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


        # chapter = Chapter(book_path, metafile, self.chapters)
        # print(chapter.get_chapters())
        # TODO check if aax or aaxc
        # TODO work with multiple audio files
        self.rebuild_chapters
        self.ffmeta.write(self.metafile)
        base_cmd = self.base_cmd
        if self.remove_intro_outro:
            start_new, duration_new = self.ffmeta.get_start_end_without_intro_outro(self.api_chapter)
            base_cmd.extend([
                "-ss",
                f"{start_new}ms",
                "-t",
                f"{duration_new}ms",
            ])
        input_file = [
            "-i",
            str(self.book_path),
        ]
        base_cmd.extend(input_file)
        base_cmd.extend([
            "-i",
            str(self.metafile),
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
            "-map_chapters",
            "1",
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

    def create_meta_file(self, ffmpeg_command: list[str], book_path: Path) -> Path:
        metafile = book_path.with_suffix(".meta")
        ffmpeg_command.extend([
            "-i",
            str(book_path),
            "-f",
            "ffmetadata",
            str(metafile),
        ])
        subprocess.run(ffmpeg_command)
        return metafile
        
