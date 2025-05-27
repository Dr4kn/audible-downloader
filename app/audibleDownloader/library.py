import audible
import json
import os
import sqlite3

def get_library(auth):
        with audible.Client(auth = auth) as client:
            library = client.get(
                "1.0/library",
                num_results=1000,
                response_groups="product_desc, product_attrs",
                sort_by="-PurchaseDate"
            )
        return library
    
class Library:
    def __init__(self, auth, path: os.path):
        self.auth = auth
        self.library = get_library(auth)
        self.path = path
        self.con = sqlite3.connect(self.path + "audiobooks.db")
        self.con.execute("""CREATE TABLE IF NOT EXISTS audiobooks (
                    asin TEXT UNIQUE,
                    authors TEXT NOT NULL,
                    title TEXT NOT NULL,
                    date_added TEXT NOT NULL,
                    subtitle TEXT,
                    series_title TEXT,
                    narrators TEXT,
                    series_sequence INT,
                    release_date TEXT,
                    downloaded INT
            );""")

    def export_library_as_json(self):
        path = self.path + "audible_library.json"
        with open(path, "w") as f:
            json.dump(self.library["items"], f)