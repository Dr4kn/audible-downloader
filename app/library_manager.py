"""
Library management module.
Handles updating and synchronizing the audiobook library.
"""

import sys
from database import db
from audible_api import audible_api


class LibraryManager:
    """Manages library updates and synchronization."""
    
    def update_library(self):
        """Update library from Audible and sync with database."""
        try:
            # Update library from Audible
            if not audible_api.update_library():
                print("Failed to update library from Audible")
                sys.stdout.flush()
                return
            
            # Read and process library data
            books_data = audible_api.get_library_data()
            if not books_data:
                print("No library data found")
                sys.stdout.flush()
                return
            
            # Add new books to database
            added_count = 0
            for book_data in books_data:
                try:
                    if db.add_book(book_data):
                        title = book_data.get('title', 'Unknown')
                        asin = book_data.get('asin', 'Unknown')
                        print(f"Added new book to database: {title} (ASIN: {asin})")
                        sys.stdout.flush()
                        added_count += 1
                        
                except Exception as e:
                    print(f"Error processing book: {e}")
                    sys.stdout.flush()
                    continue
            
            print(f"Library update complete. Added {added_count} new books.")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Error in update_library: {e}")
            sys.stdout.flush()


# Global library manager instance
library_manager = LibraryManager()