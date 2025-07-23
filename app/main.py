from audibleDownloader import Authentication
from audibleDownloader import Book
from audibleDownloader import Library
from audibleDownloader import Status
import os
from pathlib import Path

path = os.path.expanduser("~/.config/audible")
p = Path(path)
auth = Authentication(p).get_authentication()
library = Library(auth, p)
# library.add_books()
lib_list = library.get_undownloaded_books()

while len(lib_list) > 0:
    book = lib_list.pop(0)
    # book = library.get_book_data_by_asin("1508287058")
    print(book.asin)
    book.set_path(p)

    result = book.download()
#     if result == Status.ERROR:
#         break
#     library.set_book_as_downloaded(book.asin)

#     # TODO make a way of converting downloaded but not converted books. 
#     # Like when the download finished but the convertion stopped for some reason
    result = book.convert()
#     if result == Status.ERROR: 
#         break
#     if result == Status.NOT_DOWNLOADED:
#         library.set_book_as_not_downloaded(book.asin)
#         continue
#     library.set_book_as_converted(book.asin)
    book.set_metadata()
    break
# TODO check if the multiple authors are correctly read by audiobookshelf