import audible
import json
import os
import sqlite3
import re
import httpx
from .book import Book
from .metadata_guesser import MetadataGuesser
from .helper import Status
from pathlib import Path

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
    def __init__(self, auth, path: Path):
        self.auth = auth
        self.path = path
        self.con = sqlite3.connect((self.path / "audiobooks.db").resolve())
        self.con.execute("""CREATE TABLE IF NOT EXISTS audiobooks (
                    asin TEXT UNIQUE,
                    authors TEXT NOT NULL,
                    title TEXT NOT NULL,
                    subtitle TEXT,
                    series_name TEXT,
                    series_sequence TEXT,
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
                    downloaded INT,
                    converted INT,
                    moved INT
            );""")

    def export_library_as_json(self):
        path = self.path / "audible_library.json"
        with open(path.resolve(), "w") as f:
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
            metadata_guesser = MetadataGuesser(title, subtitle, series_name)
            series_sequence = None
            if metadata_guesser.guess_missing_data() is Status.SUCCESS:
                subtitle = metadata_guesser.get_subtitle()
                series_name = metadata_guesser.get_series_name()
                series_sequence = str(metadata_guesser.get_series_sequence())

            # genres are saved in multiple "ladders" with each ladder having one or more genre. Why it is that way I have no fucking idea
            genre_ladders = [category_ladders['ladder'] for category_ladders in book['category_ladders']]
            # get all the genres in each ladder, than flatten the arrays and discard every duplicate
            genres = listToString(list(set(sum([[genres['name'] for genres in ladders] for ladders in genre_ladders], []))))
            purchase_date = book['purchase_date']

            # downloadables
            product_image = book['product_images']['500']
            # pdf
            # this is a workaround described here:
            # https://audible.readthedocs.io/en/latest/misc/advanced.html
            # gets a working pdf link, but only if there is actually a pdf available
            pdf_url = None
            if book['pdf_url'] is not None:
                tld = self.auth.locale.domain

                with httpx.Client(auth=self.auth) as client:
                    resp = client.head(
                        f"https://www.audible.{tld}/companion-file/{asin}"
                    )
                    pdf_url = str(resp.url)
            try:
                self.con.cursor().execute('INSERT INTO audiobooks VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                            [asin, authors, title, subtitle, series_name, series_sequence, 
                                            description, narrators, language, publisher, publishing_date, genres,
                                            content_delivery_type, purchase_date, product_image, pdf_url, 0, 0, 0])
                self.con.commit()
            except:
                print(asin)
                print("sql write didn't work")
   
    def get_undownloaded_books(self) -> list[Book]:
        try:
            # Date should be now and before because you could have prebought books, which aren't released yet.
            books = self.con.cursor().execute("SELECT * FROM audiobooks WHERE downloaded = 0 AND publishing_date <= DATE('now')").fetchall()
            return [Book(book, self.path) for book in books]
        except:
            return ()
        
    def set_book_as_not_downloaded(self, asin: str) -> bool:
        try: 
            self.con.cursor().execute("UPDATE audiobooks SET downloaded=0 WHERE asin=?", [asin])
            self.con.commit()
            return True
        except:
            print("sql update for book not downloaded failed")
            return False
    def set_book_as_downloaded(self, asin: str) -> bool:
        try: 
            self.con.cursor().execute("UPDATE audiobooks SET downloaded=1 WHERE asin=?", [asin])
            self.con.commit()
            return True
        except:
            print("sql update for book downloaded failed")
            return False

    def set_book_as_not_converted(self, asin: str) -> bool:
        try: 
            self.con.cursor().execute("UPDATE audiobooks SET converted=0 WHERE asin=?", [asin])
            self.con.commit()
            return True
        except:
            print("sql update for book not converted failed")
            return False

    def set_book_as_converted(self, asin: str) -> bool:
        try: 
            self.con.cursor().execute("UPDATE audiobooks SET converted=1 WHERE asin=?", [asin])
            self.con.commit()
            return True
        except:
            print("sql update for book converted failed")
            return False

    def set_book_as_moved(self, asin: str) -> bool:
        try: 
            self.con.cursor().execute("UPDATE audiobooks SET moved=1 WHERE asin=?", [asin])
            self.con.commit()
            return True
        except:
            print("sql update for book moved failed")
            return False
    
    def get_book_data_by_asin(self, asin: str) -> Book:
        return Book(self.con.cursor().execute("SELECT * FROM audiobooks WHERE asin=?", [asin]).fetchone())
