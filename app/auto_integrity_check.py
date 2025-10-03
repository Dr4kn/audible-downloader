#!/usr/bin/env python3
"""
Automated Integrity Check and Fix for Audiobook Downloader

This is a streamlined version of the integrity verification tool
designed for automatic integration with the main downloader.
It performs essential checks and fixes without verbose output.
"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

# Configuration - matches main script
config = "/config"
audiobook_directory = "/audiobooks"
use_folders = True if os.getenv('AUDIOBOOK_FOLDERS') == "True" else False

def verify_and_fix():
    """Perform integrity verification and automatic fixes."""
    try:
        con = sqlite3.connect(config + "/audiobooks.db")
        cur = con.cursor()
        
        # Get books marked as downloaded
        books = cur.execute('''
            SELECT asin, title, authors FROM audiobooks WHERE downloaded = 1
        ''').fetchall()
        
        missing_asins = []
        corrupted_files = []
        issues_found = 0
        
        print(f"🔍 Checking {len(books)} downloaded books...")
        
        for asin, title, authors in books:
            # Quick check for file existence using glob pattern
            found_files = []
            
            # Search for audiobook files with this ASIN
            for root, dirs, files in os.walk(audiobook_directory):
                for file in files:
                    if file.startswith(asin) and file.endswith(('.m4b', '.aax', '.aaxc')):
                        filepath = os.path.join(root, file)
                        found_files.append(filepath)
            
            if not found_files:
                missing_asins.append(asin)
                issues_found += 1
                print(f"   📋 Missing: {title} by {authors}")
            else:
                # Quick integrity check using file size (corrupted files are often 0 bytes or very small)
                for filepath in found_files:
                    try:
                        file_size = os.path.getsize(filepath)
                        if file_size < 1024 * 1024:  # Less than 1MB is likely corrupted
                            corrupted_files.append({
                                'asin': asin,
                                'file': filepath,
                                'book': f"{title} by {authors}"
                            })
                            issues_found += 1
                            print(f"   🔥 Corrupted: {title} by {authors} (size: {file_size} bytes)")
                    except OSError:
                        # File exists in directory listing but can't be accessed
                        corrupted_files.append({
                            'asin': asin,
                            'file': filepath,
                            'book': f"{title} by {authors}"
                        })
                        issues_found += 1
                        print(f"   🔥 Inaccessible: {title} by {authors}")
        
        # Apply fixes
        if issues_found > 0:
            print(f"🔧 Fixing {issues_found} issues...")
            fixed = 0
            
            # Fix missing files
            for asin in missing_asins:
                try:
                    cur.execute('UPDATE audiobooks SET downloaded = 0 WHERE asin = ?', [asin])
                    fixed += 1
                except sqlite3.Error as e:
                    print(f"   ❌ Error resetting ASIN {asin}: {e}")
            
            # Fix corrupted files
            for item in corrupted_files:
                try:
                    # Remove corrupted file
                    if os.path.exists(item['file']):
                        os.remove(item['file'])
                    
                    # Reset download status
                    cur.execute('UPDATE audiobooks SET downloaded = 0 WHERE asin = ?', [item['asin']])
                    fixed += 1
                except (OSError, sqlite3.Error) as e:
                    print(f"   ❌ Error fixing {item['asin']}: {e}")
            
            con.commit()
            print(f"✅ Fixed {fixed} issues - books will be re-downloaded")
        else:
            print("✅ No issues found")
        
        con.close()
        return issues_found
        
    except Exception as e:
        print(f"❌ Error during integrity check: {e}")
        return -1

if __name__ == "__main__":
    sys.exit(verify_and_fix())