from .auth import authenticator        
import audible

def get_library():
    auth = authenticator()
    with audible.Client(auth=auth) as client:
        library = client.get(
            "1.0/library",
            num_results=1000,
            response_groups="product_desc, product_attrs",
            sort_by="-PurchaseDate"
        )
        for book in library["items"]:
            print(book)
            print("")