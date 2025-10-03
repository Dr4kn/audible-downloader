"""
File processing module.
Handles audiobook file conversion, organization, and cleanup.
"""

import os
import shutil
import subprocess
import sys
from typing import Optional, List
from config import AUDIOBOOK_DOWNLOAD_DIR, AUDIOBOOK_DIR, USE_FOLDERS
from database import db


class FileProcessor:
    """Manages audiobook file processing and organization."""
    
    def process_downloaded_files(self):
        """Process all downloaded audiobook files."""
        try:
            audiobooks = self._get_downloaded_files()
            if not audiobooks:
                return
            
            for audiobook in audiobooks:
                self._process_single_file(audiobook)
                
        except OSError as e:
            print(f"Error accessing download directory: {e}")
            sys.stdout.flush()
    
    def _get_downloaded_files(self) -> List[str]:
        """Get list of downloaded audiobook files."""
        try:
            return [f for f in os.listdir(AUDIOBOOK_DOWNLOAD_DIR) 
                   if f.endswith(('.aax', '.aaxc'))]
        except OSError:
            return []
    
    def _process_single_file(self, audiobook_file: str):
        """Process a single audiobook file."""
        try:
            print(f"Processing file: {audiobook_file}")
            sys.stdout.flush()
            
            # Extract ASIN from filename
            asin = audiobook_file.split("_")[0]
            
            # Validate ASIN exists in database
            if not self._validate_asin(asin, audiobook_file):
                return
            
            # Update database to mark as downloaded
            db.mark_downloaded(asin)
            
            # Process the audio file
            self._convert_and_organize(audiobook_file, asin)
            
        except Exception as e:
            print(f"Error processing {audiobook_file}: {e}")
            sys.stdout.flush()
    
    def _validate_asin(self, asin: str, audiobook_file: str) -> bool:
        """Validate that the ASIN exists in our database."""
        book_info = db.get_book_info(asin)
        
        if book_info is None:
            # Try to find the original ASIN from the download request
            original_asin = self._find_original_asin(audiobook_file)
            if original_asin and db.get_book_info(original_asin):
                # Rename file to match database ASIN
                new_name = audiobook_file.replace(asin, original_asin)
                try:
                    old_path = os.path.join(AUDIOBOOK_DOWNLOAD_DIR, audiobook_file)
                    new_path = os.path.join(AUDIOBOOK_DOWNLOAD_DIR, new_name)
                    shutil.move(old_path, new_path)
                    print(f"Renamed file to match database ASIN: {new_name}")
                    sys.stdout.flush()
                    return True
                except OSError as e:
                    print(f"Error renaming file {audiobook_file}: {e}")
                    return False
            else:
                print(f"Warning: Cannot find ASIN {asin} in database. Skipping file {audiobook_file}")
                return False
        
        return True
    
    def _find_original_asin(self, audiobook_file: str) -> Optional[str]:
        """Try to find the original ASIN that was requested for download."""
        # This is a placeholder - in practice, you might need to implement
        # logic to track the original ASIN from the download request
        return None
    
    def _convert_and_organize(self, audiobook_file: str, asin: str):
        """Convert and organize the audiobook file."""
        try:
            src_path = os.path.join(AUDIOBOOK_DOWNLOAD_DIR, audiobook_file)
            
            # Remove file extension to get base name
            if audiobook_file.endswith('.aax'):
                base_name = audiobook_file[:-4]  # Remove .aax (4 characters)
            elif audiobook_file.endswith('.aaxc'):
                base_name = audiobook_file[:-5]  # Remove .aaxc (5 characters)
            else:
                base_name = os.path.splitext(audiobook_file)[0]  # Generic fallback
            
            # Create destination folder if using folder structure
            if USE_FOLDERS:
                dest_folder = self._create_audiobook_folder(asin)
                if not dest_folder:
                    print(f"Skipping {base_name} - could not create folder structure")
                    return
                dest_path = os.path.join(dest_folder, base_name + ".m4b")
            else:
                dest_path = os.path.join(AUDIOBOOK_DIR, base_name + ".m4b")
            
            print(f"Converting {src_path} -> {dest_path}")
            sys.stdout.flush()
            
            # Remove existing file if it exists
            if os.path.exists(dest_path):
                print(f"Removing existing file: {os.path.basename(dest_path)}")
                try:
                    os.remove(dest_path)
                except OSError as e:
                    print(f"Error removing existing file: {e}")
                    return
            
            # Convert the file
            self._convert_audiobook(src_path, dest_path)
            
        except Exception as e:
            print(f"Error converting and organizing {audiobook_file}: {e}")
            sys.stdout.flush()
    
    def _create_audiobook_folder(self, asin: str) -> Optional[str]:
        """Create the appropriate folder structure for an audiobook."""
        try:
            book_info = db.get_book_info(asin)
            if not book_info:
                return None
            
            # This is a simplified version - you might want to implement
            # more sophisticated folder creation logic based on metadata
            folder_path = os.path.join(AUDIOBOOK_DIR, asin)
            os.makedirs(folder_path, exist_ok=True)
            return folder_path
            
        except Exception as e:
            print(f"Error creating folder for {asin}: {e}")
            return None
    
    def _convert_audiobook(self, src_path: str, dest_path: str):
        """Convert audiobook using FFmpeg."""
        try:
            print(f"Converting audiobook: {os.path.basename(src_path)}")
            sys.stdout.flush()
            
            # Get activation bytes from the API
            from audible_api import audible_api
            activation_bytes = audible_api.activation_bytes
            
            # FFmpeg conversion command
            cmd = [
                "ffmpeg", "-y", 
                "-activation_bytes", activation_bytes,
                "-i", src_path,
                "-c", "copy",
                dest_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully converted: {os.path.basename(dest_path)}")
                # Remove source file after successful conversion
                os.remove(src_path)
                print(f"Removed source file: {os.path.basename(src_path)}")
            else:
                print(f"Error converting {os.path.basename(src_path)}: {result.stderr}")
            
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Error in FFmpeg conversion: {e}")
            sys.stdout.flush()
    
    def cleanup_temp_files(self):
        """Clean up temporary files and vouchers."""
        try:
            vouchers = [f for f in os.listdir(AUDIOBOOK_DOWNLOAD_DIR) 
                       if f.endswith('.voucher')]
            
            for voucher in vouchers:
                try:
                    voucher_path = os.path.join(AUDIOBOOK_DOWNLOAD_DIR, voucher)
                    os.remove(voucher_path)
                    print(f"Cleaned up remaining voucher: {voucher}")
                except OSError as e:
                    print(f"Error removing voucher {voucher}: {e}")
                    
        except OSError as e:
            print(f"Error accessing download directory for cleanup: {e}")


# Global file processor instance
file_processor = FileProcessor()