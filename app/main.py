"""
Main orchestration module for the audiobook downloader.
Coordinates all components and handles the main workflow.
"""

import sys
from library_manager import library_manager
from restriction_checker import restriction_checker
from integrity_checker import integrity_checker
from downloader import downloader
from file_processor import file_processor


class AudiobookDownloaderApp:
    """Main application class that orchestrates the entire workflow."""
    
    def run(self):
        """Execute the complete audiobook download workflow."""
        try:
            print("Starting audiobook downloader...")
            sys.stdout.flush()
            
            # Step 1: Update library from Audible
            library_manager.update_library()
            
            # Step 2: Check downloadability for new books
            restriction_checker.check_all_restrictions()
            
            # Step 3: Run integrity verification and auto-fix
            integrity_checker.run_integrity_check_and_fix()
            
            # Step 4: Download new/fixed titles
            downloader.download_new_titles()
            
            # Step 5: Process downloaded files
            file_processor.process_downloaded_files()
            
            # Step 6: Clean up temporary files
            file_processor.cleanup_temp_files()
            
            print("Audiobook downloader cycle completed successfully.")
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            print("Process interrupted by user.")
            sys.stdout.flush()
        except Exception as e:
            print(f"Unexpected error in main: {e}")
            print("The process will continue on the next cycle...")
            sys.stdout.flush()


def main():
    """Entry point for the application."""
    app = AudiobookDownloaderApp()
    app.run()


if __name__ == "__main__":
    main()