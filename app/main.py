from audibleDownloader import auth
from audibleDownloader import Library

library = Library(auth.get_authentication())
library.export_library_as_json()
