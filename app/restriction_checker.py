"""
Download restriction checker module.
Handles detection of Audible Plus and other download restrictions.
"""

import sys
from typing import List, Tuple
from config import API_BATCH_SIZE
from database import db
from audible_api import audible_api


class RestrictionChecker:
    """Handles checking and updating download restrictions for audiobooks."""
    
    def check_all_restrictions(self):
        """Check and update downloadability status for unchecked books."""
        try:
            print("🔍 Checking download restrictions for new books...")
            sys.stdout.flush()
            
            unchecked_books = db.get_unchecked_books()
            
            if not unchecked_books:
                print("   All books already checked for download restrictions")
                sys.stdout.flush()
                return
            
            print(f"   Checking {len(unchecked_books)} books for download restrictions...")
            sys.stdout.flush()
            
            # Process books in batches
            for i in range(0, len(unchecked_books), API_BATCH_SIZE):
                batch = unchecked_books[i:i+API_BATCH_SIZE]
                self._process_batch(batch)
                
        except Exception as e:
            print(f"Error in check_all_restrictions: {e}")
            sys.stdout.flush()
    
    def _process_batch(self, batch: List[Tuple[str, str]]):
        """Process a batch of books for restriction checking."""
        asins = [book[0] for book in batch]
        
        # Try batch API call first
        api_data = audible_api.get_book_details(asins)
        
        if api_data and api_data.get('items'):
            # Batch call succeeded
            self._process_batch_response(api_data['items'])
        else:
            # Batch failed, try individual calls
            print(f"   Batch API call failed, checking individual ASINs...")
            sys.stdout.flush()
            self._process_individual_books(batch)
    
    def _process_batch_response(self, items: List[dict]):
        """Process successful batch API response."""
        for item in items:
            asin = item.get('asin')
            title = item.get('title', 'Unknown')
            is_downloadable, reason = self._analyze_book_restrictions(item)
            
            self._update_book_status(asin, title, is_downloadable, reason)
    
    def _process_individual_books(self, batch: List[Tuple[str, str]]):
        """Process books individually when batch calls fail."""
        for asin, title in batch:
            try:
                book_data = audible_api.get_single_book_details(asin)
                
                if book_data:
                    is_downloadable, reason = self._analyze_book_restrictions(book_data)
                    self._update_book_status(asin, title, is_downloadable, reason)
                else:
                    # No API data available
                    print(f"   ❓ {title} (ASIN: {asin}) - No API data available")
                    db.update_downloadability(asin, False, "No API data available (may be invalid ASIN)")
                    
            except Exception as e:
                print(f"   ❌ {title} (ASIN: {asin}) - Error: {e}")
                db.update_downloadability(asin, False, f"Error during check: {e}")
                
            sys.stdout.flush()
    
    def _analyze_book_restrictions(self, book_data: dict) -> Tuple[bool, str]:
        """Analyze book data to determine if it has download restrictions."""
        is_ayce = book_data.get('is_ayce', False)
        benefit_id = book_data.get('benefit_id')
        
        # Check for Audible Plus restrictions
        if is_ayce or benefit_id == "AYCL":
            return False, "Audible Plus catalog book (streaming only)"
        
        # Check for other potential restrictions
        is_purchasability_suppressed = book_data.get('is_purchasability_suppressed', False)
        if is_purchasability_suppressed:
            return False, "Purchase suppressed by publisher"
        
        # Add more restriction checks here as needed
        
        # Book appears to be downloadable
        return True, None
    
    def _update_book_status(self, asin: str, title: str, is_downloadable: bool, reason: str):
        """Update book status in database and log the result."""
        db.update_downloadability(asin, is_downloadable, reason)
        
        if is_downloadable:
            print(f"   ✅ {title} (ASIN: {asin}) - Downloadable")
        else:
            print(f"   ⚠️  {title} (ASIN: {asin}) - {reason}")
        
        sys.stdout.flush()


# Global restriction checker instance
restriction_checker = RestrictionChecker()