"""
Audible API interaction module.
Handles all interactions with the Audible CLI and API calls.
"""

import subprocess
import json
import os
import sys
from typing import Dict, List, Optional
from config import CONFIG_DIR, AUDIBLE_TIMEOUT, FILENAME_MODE, AUDIOBOOK_DOWNLOAD_DIR


class AudibleAPI:
    """Manages interactions with the Audible CLI."""
    
    def __init__(self):
        self.activation_bytes = self._get_activation_bytes()
    
    def _get_activation_bytes(self) -> str:
        """Get and validate activation bytes."""
        try:
            # Get activation bytes
            subprocess.run(["audible", "activation-bytes"], check=True)
            
            # Find the JSON file with activation bytes
            json_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
            if not json_files:
                raise Exception("No activation bytes JSON file found")
            
            with open(os.path.join(CONFIG_DIR, json_files[0]), 'r') as f:
                data = json.load(f)
                activation_bytes = data.get("activation_bytes")
            
            if not activation_bytes:
                raise Exception("No activation bytes found in JSON file")
            
            return activation_bytes
            
        except Exception as e:
            print(f"Error getting activation bytes: {e}")
            sys.stdout.flush()
            raise
    
    def update_library(self) -> bool:
        """Update library from Audible and return success status."""
        try:
            print("Updating library from Audible...")
            sys.stdout.flush()
            
            # Use the JSON API approach instead of export
            return True  # We'll get data directly in get_library_data
            
        except Exception as e:
            print(f"Error updating library: {e}")
            sys.stdout.flush()
            return False
    
    def get_library_data(self) -> List[Dict]:
        """Get library data directly from Audible CLI JSON API."""
        try:
            # Use Audible CLI to get library as JSON (simplified approach)
            result = subprocess.run(
                ["audible", "library", "list"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"Error getting library: {result.stderr}")
                sys.stdout.flush()
                return []
            
            # Try to parse as JSON if available, otherwise parse the text output
            try:
                library_data = json.loads(result.stdout)
                items = library_data.get("items", [])
            except json.JSONDecodeError:
                # If not JSON, parse the text output format
                print("Parsing library text output...")
                sys.stdout.flush()
                items = self._parse_library_text_output(result.stdout)
            
            # Convert to the format expected by the database
            books = []
            for item in items:
                if isinstance(item, dict):
                    book = {
                        'title': item.get('title', ''),
                        'authors': ', '.join([author.get('name', '') for author in item.get('authors', [])]) if item.get('authors') else item.get('authors', ''),
                        'asin': item.get('asin', '')
                    }
                    books.append(book)
            
            return books
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"Error getting library: {e}")
            sys.stdout.flush()
            return []
        except Exception as e:
            print(f"Error reading library: {e}")
            sys.stdout.flush()
            return []
    
    def _parse_library_text_output(self, output: str) -> List[Dict]:
        """Parse text-based library output if JSON is not available."""
        # This is a fallback - in practice, we may need to implement based on actual output format
        # For now, return empty list and let the system continue
        print("Text parsing not yet implemented - using empty library")
        sys.stdout.flush()
        return []
    
    def get_book_details(self, asins: List[str]) -> Optional[Dict]:
        """Get detailed book information from the API."""
        try:
            asin_list = ','.join(asins)
            result = subprocess.run([
                "audible", "api", "1.0/library",
                "-p", f"asins={asin_list}",
                "-p", "response_groups=product_desc,product_attrs",
                "-f", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            return None
            
        except Exception as e:
            print(f"Error getting book details: {e}")
            sys.stdout.flush()
            return None
    
    def get_single_book_details(self, asin: str) -> Optional[Dict]:
        """Get detailed information for a single book."""
        try:
            result = subprocess.run([
                "audible", "api", "1.0/library",
                "-p", f"asins={asin}",
                "-p", "response_groups=product_desc,product_attrs",
                "-f", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                items = data.get('items', [])
                return items[0] if items else None
            return None
            
        except Exception as e:
            print(f"Error getting single book details for {asin}: {e}")
            sys.stdout.flush()
            return None
    
    def download_book(self, asin: str) -> bool:
        """Download a book by ASIN."""
        try:
            print(f"Downloading audiobook with ASIN: {asin}")
            sys.stdout.flush()
            
            result = subprocess.run([
                "audible", "-v", "error", "download", 
                "-a", asin, 
                "--aax-fallback", 
                "--timeout", AUDIBLE_TIMEOUT, 
                "-f", FILENAME_MODE, 
                "--ignore-podcasts", 
                "-o", AUDIOBOOK_DOWNLOAD_DIR
            ])
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error downloading {asin}: {e}")
            sys.stdout.flush()
            return False
    
    def check_download_error(self, asin: str) -> Optional[str]:
        """Check if a download attempt returns a specific error message."""
        try:
            result = subprocess.run(
                ["audible", "download", "-a", asin, "--aax-fallback"], 
                capture_output=True, text=True, timeout=30
            )
            
            if "is not downloadable" in result.stdout:
                return "Detected as non-downloadable during download attempt"
            
            return None
            
        except Exception:
            return None


# Global API instance
audible_api = AudibleAPI()