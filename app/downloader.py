"""
Core download logic module.
Handles the main download workflow and coordination.
"""

import sys
from datetime import datetime
from typing import List, Tuple
from database import db
from audible_api import audible_api
from restriction_checker import restriction_checker


class AudiobookDownloader:
    """Manages the core audiobook download workflow."""
    
    def download_new_titles(self):
        """Download all available and downloadable audiobooks."""
        try:
            # Get downloadable and restricted books
            downloadable_books = db.get_downloadable_books()
            restricted_books = db.get_restricted_books()
            
            # Report restricted books
            if restricted_books:
                self._report_restricted_books(restricted_books)
            
            # Check if there are downloadable books
            if not downloadable_books:
                print("No downloadable books found that haven't been downloaded yet.")
                sys.stdout.flush()
                return
            
            print(f"Found {len(downloadable_books)} downloadable books to process.")
            sys.stdout.flush()
            
            # Process each downloadable book
            for asin, title, _ in downloadable_books:
                self._download_single_book(asin, title)
                
        except Exception as e:
            print(f"Error in download_new_titles: {e}")
            sys.stdout.flush()
    
    def _report_restricted_books(self, restricted_books: List[Tuple[str, str, str]]):
        """Report books that are being skipped due to restrictions."""
        print(f"\n📋 Skipping {len(restricted_books)} non-downloadable books:")
        sys.stdout.flush()
        
        for asin, title, reason in restricted_books:
            print(f"   ⚠️  {title} (ASIN: {asin}) - {reason or 'Unknown restriction'}")
            sys.stdout.flush()
        print()
    
    def _download_single_book(self, asin: str, title: str):
        """Download a single audiobook and handle errors."""
        try:
            # Update last download attempt timestamp
            timestamp = datetime.now().isoformat()
            db.update_download_attempt(asin, timestamp)
            
            # Attempt download
            success = audible_api.download_book(asin)
            
            if not success:
                print(f"Download failed for ASIN {asin} (exit code: non-zero)")
                sys.stdout.flush()
                
                # Check if it's actually not downloadable
                error_reason = audible_api.check_download_error(asin)
                if error_reason:
                    print(f"   Detected download restriction for {title} - updating database")
                    db.update_downloadability(asin, False, error_reason)
                    sys.stdout.flush()
                
                return False
            
            return True
            
        except Exception as e:
            print(f"Error downloading {asin}: {e}")
            sys.stdout.flush()
            return False


# Global downloader instance
downloader = AudiobookDownloader()