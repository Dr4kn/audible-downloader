from pathlib import Path
from .book import Book
from .plugins.cmd_decrypt import FFMeta, ApiChapterInfo, _get_voucher_filename, _get_chapter_filename
import subprocess

class Decyrpter:
    def __init__(self, book: Book, activation_bytes: str, remove_intro_outro = True):
        self.book = book
        self.activation_bytes = activation_bytes
        self.books = []
        self.cover, self.voucher = None, None
        self.remove_intro_outro = remove_intro_outro
        for file in list(self.book.audiobook_download_directory.iterdir()):
            match file.suffix:
                case ".aax":
                    self.books.append(file)
                case ".aaxc":
                    self.books.append(file)
                case ".jpg":
                    self.cover = file
                case ".voucher":
                    self.voucher = file

        # audible cmd_decyrpt
        self._api_chapter = None
        # TODO multiple input files
        self._source = None
        self.ffmeta = None

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
        print(self.api_chapter)
        self.ffmeta.update_chapters_from_chapter_info(
            self.api_chapter, True, False, self.remove_intro_outro
        )

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

    def decrypt(self):
        # TODO check if aax or aaxc
        # TODO work with multiple audio files
        for book in self.books:
            base_cmd = self.base_cmd
            metafile = self.create_meta_file(base_cmd, book)
            base_cmd = self.base_cmd # without this metafile would add to the command
            self.ffmeta = FFMeta(metafile)
            self._source = book
            sucessfull_rebuild = True
            try:
                self.rebuild_chapters
            except:
                sucessfull_rebuild = False
            self.ffmeta.write(metafile)
            if sucessfull_rebuild and self.remove_intro_outro:
                start_new, duration_new = self.ffmeta.get_start_end_without_intro_outro(self.api_chapter)
                base_cmd.extend([
                    "-ss",
                    f"{start_new}ms",
                    "-t",
                    f"{duration_new}ms",
                ])
            input_file = [
                "-i",
                str(book),
            ]
            base_cmd.extend(input_file)
            base_cmd.extend([
                "-i",
                str(metafile),
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
            ]
            
            metadata = [
                ["title", self.book.title],
                ["artist", self.book.authors],
                ["album_artist", self.book.authors],
                ["album", self.book.title],
                ["genre", self.book.genres],
                ["date", self.book.publishing_date],
                ["comment", self.book.description],
                ["description", self.book.description],
                ["composer", self.book.narrators],
                ["publisher", self.book.publisher],
                ["language", self.book.language],
            ]
            if self.book.subtitle is not None:
                metadata.append(["TIT3", self.book.subtitle])
            if self.book.series_name is not None:
                metadata.append(["series", self.book.series_name])
            if self.book.series_sequence is not None:
                metadata.append(["series-part", self.book.series_sequence])
            for tag in metadata:
                set_metadata.extend(
                    [
                        "-metadata",
                        str(tag[0]) + "=" + str(tag[1]),
                    ]
                )
            base_cmd.extend(set_metadata)
            faststart = [ # can slighlty improve playback performance when streaming.
                "-movflags", 
                "+faststart",
            ]
            base_cmd.extend(faststart)
            book_without_asin_prefix = book.name.split("_", 1)[1]
            outputfile = [
                "-c",
                "copy",
                book.with_name(book_without_asin_prefix).with_suffix(".m4b"),

            ]
            base_cmd.extend(outputfile)
            subprocess.run(base_cmd)