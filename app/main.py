from audibleDownloader import Authentication
from audibleDownloader import Library
import os

path = os.path.expanduser("~/.config/audible/")
library = Library(Authentication(path).get_authentication())
library.export_library_as_json()
