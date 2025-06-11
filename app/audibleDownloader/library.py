import audible
import json
import os
import sqlite3
import re

def get_library(auth):
    with audible.Client(auth = auth) as client:
        library = client.get(
            "1.0/library",
            num_results=1000,
            sort_by="-PurchaseDate"
        )
    return library

def listToString(input: list): 
    stringList = ""
    for i in range(0, len(input)):
        stringList += input[i]
        if (i != len(input) - 1):
            stringList += ";"
    return stringList

class Library:
    def __init__(self, auth, path: os.path):
        self.auth = auth
        self.path = path
        self.con = sqlite3.connect(self.path + "audiobooks.db")
        self.con.execute("""CREATE TABLE IF NOT EXISTS audiobooks (
                    asin TEXT UNIQUE,
                    authors TEXT NOT NULL,
                    title TEXT NOT NULL,
                    subtitle TEXT,
                    series_name TEXT,
                    series_sequence INT,
                    description TEXT,
                    narrators TEXT,
                    language TEXT,
                    publisher TEXT,
                    publishing_date TEXT,
                    genres TEXT,
                    content_delivery_type TEXT,
                    purchase_date TEXT NOT NULL,
                    product_image TEXT,
                    pdf_url TEXT,
                    downloaded INT
            );""")

    def export_library_as_json(self):
        path = self.path + "audible_library.json"
        with open(path, "w") as f:
            json.dump(get_library(self.auth)["items"], f)

    # https://www.audiobookshelf.org/docs#book-directory-structure
    def add_books(self):
        for book in get_library(self.auth)["items"]:
            asin = book['asin']
            authors = listToString([author['name'] for author in book["authors"]])
            title = book['title']
            subtitle = book['subtitle']
            # descriptions sometimes have unwanted <x> </x> html tags or might end in three or more dots.
            pattern = r"</?[a-zA-Z]>|\.{3,}"
            description = re.sub(pattern, "", book['merchandising_summary'])

            narrators = listToString([narrator['name'] for narrator in book['narrators']])
            language = book['language']
            publisher = book['publisher_name']
            publishing_date = book['release_date'] # format YYYY-MM-DD
            content_delivery_type = book['content_delivery_type'] # SinglePartBook, MultiPartBook, Periodical, 
            series_name = book['publication_name']

            # genres are saved in multiple "ladders" with each ladder having one or more genre. Why it is that way I have no fucking idea
            genre_ladders = [category_ladders['ladder'] for category_ladders in book['category_ladders']]
            # get all the genres in each ladder, than flatten the arrays and discard every duplicate
            genres = listToString(list(set(sum([[genres['name'] for genres in ladders] for ladders in genre_ladders], []))))

            purchase_date = book['purchase_date']
            # downloadables
            product_image = book['product_images']['500']
            pdf_url = book['pdf_url']
            # thesaurus_subject_keywords = book['thesaurus_subject_keywords']
            
            try:
                self.con.cursor().execute('INSERT INTO audiobooks values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                            [asin, authors, title, subtitle, series_name, 0, 
                                            description, narrators, language, publisher, publishing_date, genres,
                                            content_delivery_type, purchase_date, product_image, pdf_url, 0])
                self.con.commit()
            except:
                break
    
    def get_undownloaded_book(self) -> list:
        try:
            return self.con.cursor().execute("SELECT * FROM audiobooks WHERE downloaded = 0 LIMIT 1").fetchone()
        except:
            return ()
        
    def set_book_as_downloaded(self, asin: str) -> bool:
        try: 
            self.con.cursor().execute("UPDATE audiobooks SET downloaded=1 WHERE asin=?", [asin])
            self.con.commit()
            return True
        except:
            return False
    
    def get_book_data_by_asin(self, asin: str) -> list:
        return self.con.cursor().execute("SELECT * FROM audiobooks WHERE asin=?", [asin]).fetchone()