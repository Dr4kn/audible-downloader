from audibleDownloader import Authentication
from audibleDownloader import Book
from audibleDownloader import Library
from audibleDownloader import Downloader
from audibleDownloader import Status
import os

path = os.path.expanduser("~/.config/audible/")
auth = Authentication(path).get_authentication()
library = Library(auth, path)
# library.add_books()
lib_list = library.get_undownloaded_books()

while len(lib_list) > 0:
    book = lib_list.pop(0)
    print(book.asin)
    downloader = Downloader(path, book.asin)

    result = downloader.download()
    if result == Status.ERROR:
        break
    library.set_book_as_downloaded(book.asin)

    # TODO make a way of converting downloaded but not converted books. 
    # Like when the download finished but the convertion stopped for some reason
    result = downloader.convert()
    if result == Status.ERROR: 
        break
    if result == Status.NOT_DOWNLOADED:
        library.set_book_as_not_downloaded(book.asin)
        continue
    library.set_book_as_converted(book.asin)
