import audible
from .auth import get_authentication
import json
import os

def get_library(auth):
        with audible.Client(auth = auth) as client:
            library = client.get(
                "1.0/library",
                num_results=1000,
                response_groups="product_desc, product_attrs",
                sort_by="-PurchaseDate"
            )
class Library:
    def __init__(self, auth):
        self.auth = auth
        self.library = get_library(auth)

    def export_library_as_json(self):
        path = os.path.expanduser("~/.config/audible/audible_library.json")
        with open(path, "w") as f:
            json.dump(self.library["items"], f)

