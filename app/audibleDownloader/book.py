from .helper import Status

class Book:
    def __init__(self, book: list):
        self.asin = book[0]
        self.authors = book[1]
        self.title = book[2]
        self.subtitle = book[3]
        self.series_name = book[4]
        self.series_sequence = book[5]
        self.description = book[6]
        self.narrators = book[7]
        self.language = book[8]
        self.publisher = book[9]
        self.publishing_date = book[10]
        self.genres = book[11]
        self.content_delivery_type = book[12]
        self.purchase_date = book[13]
        self.product_image = book[14]
        self.pdf_url = book[15]
        if book[16] == 0:
            self.status = Status.NOT_DOWNLOADED
        elif book[17] == 0:
            self.status = Status.DOWNLOADED
        elif book[18] == 0:
            self.status = Status.CONVERTED
        elif book[18] == 1:
            self.status = Status.MOVED
        else:
            self.status = Status.ERROR
