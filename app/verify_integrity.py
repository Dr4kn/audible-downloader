#!/usr/bin/env python3
"""
Audiobook Integrity Verification Utility

This script verifies the integrity of all audiobook files in the database by:
1. Checking if database records have corresponding files
2. Verifying file accessibility and basic metadata
3. Checking for orphaned files not in the database
4. Validating file formats and basic structure
5. Reporting statistics and any issues found
"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import argparse

# Configuration - matches main script
config = "/config"
audiobook_directory = "/audiobooks"
use_folders = True if os.getenv('AUDIOBOOK_FOLDERS') == "True" else False

def create_audiobook_path(authors, title, series_title, subtitle, narrators, series_sequence, release_date):
    """Generate the expected file path for an audiobook based on database metadata."""
    def sanitize_name(name):
        if name is None:
            return ""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '-')
        return name.strip()

    authors = sanitize_name(authors) or "Unknown Author"
    title = sanitize_name(title) or "Unknown Title"
    series_title = sanitize_name(series_title)
    subtitle = sanitize_name(subtitle)
    narrators = sanitize_name(narrators) or "Unknown Narrator"
    
    if use_folders:
        directory = audiobook_directory + "/" + authors + "/"
        if series_title and series_sequence:
            directory = directory + series_title + "/" + str(series_sequence) + " - "
        
        year = release_date.split("-")[0] if release_date and "-" in release_date else release_date or "Unknown"
        directory = directory + year + " - " + title
        
        if subtitle:
            directory = directory + " - " + subtitle
        directory = directory + " {" + narrators + "}/"
        
        return directory
    else:
        return audiobook_directory + "/"

def find_audiobook_files(base_path, asin):
    """Find all possible audiobook files for a given ASIN."""
    files = []
    extensions = ['.m4b', '.aax', '.aaxc']
    
    if os.path.exists(base_path):
        for root, dirs, filenames in os.walk(base_path):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    if asin in filename:
                        files.append(os.path.join(root, filename))
    
    return files

def verify_file_integrity(filepath):
    """Verify basic file integrity using ffprobe."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', filepath
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            format_info = data.get('format', {})
            streams = data.get('streams', [])
            
            # Basic checks
            duration = float(format_info.get('duration', 0))
            has_audio = any(stream.get('codec_type') == 'audio' for stream in streams)
            
            return {
                'valid': True,
                'duration': duration,
                'has_audio': has_audio,
                'format': format_info.get('format_name', 'unknown'),
                'size': int(format_info.get('size', 0)),
                'bitrate': format_info.get('bit_rate', 'unknown')
            }
        else:
            return {
                'valid': False,
                'error': result.stderr or 'Unknown ffprobe error'
            }
    except subprocess.TimeoutExpired:
        return {'valid': False, 'error': 'Timeout during verification'}
    except json.JSONDecodeError:
        return {'valid': False, 'error': 'Invalid ffprobe output'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def scan_orphaned_files():
    """Find audiobook files that aren't tracked in the database."""
    orphaned = []
    
    if not os.path.exists(audiobook_directory):
        return orphaned
    
    # Get all ASINs from database
    con = sqlite3.connect(config + "/audiobooks.db")
    cur = con.cursor()
    db_asins = set()
    
    try:
        for row in cur.execute('SELECT asin FROM audiobooks').fetchall():
            db_asins.add(row[0])
    except sqlite3.Error as e:
        print(f"Database error while getting ASINs: {e}")
        return orphaned
    finally:
        con.close()
    
    # Scan for audiobook files
    extensions = ['.m4b', '.aax', '.aaxc']
    for root, dirs, files in os.walk(audiobook_directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                
                # Try to extract ASIN from filename
                potential_asin = file.split('_')[0] if '_' in file else None
                
                if potential_asin and potential_asin not in db_asins:
                    orphaned.append({
                        'file': filepath,
                        'asin': potential_asin,
                        'size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    })
    
    return orphaned

def fix_missing_files(missing_asins, dry_run=False):
    """Reset download status for missing files so they get re-downloaded."""
    if not missing_asins:
        return 0
    
    print(f"\n🔧 {'Would reset' if dry_run else 'Resetting'} download status for {len(missing_asins)} missing files...")
    
    if dry_run:
        for asin in missing_asins:
            print(f"   Would reset ASIN: {asin}")
        return len(missing_asins)
    
    try:
        con = sqlite3.connect(config + "/audiobooks.db")
        cur = con.cursor()
        
        fixed = 0
        for asin in missing_asins:
            try:
                cur.execute('UPDATE audiobooks SET downloaded = 0 WHERE asin = ?', [asin])
                book_info = cur.execute('SELECT title, authors FROM audiobooks WHERE asin = ?', [asin]).fetchone()
                if book_info:
                    print(f"   ✅ Reset: {book_info[0]} by {book_info[1]} (ASIN: {asin})")
                    fixed += 1
            except sqlite3.Error as e:
                print(f"   ❌ Error resetting ASIN {asin}: {e}")
        
        con.commit()
        con.close()
        
        print(f"✅ Successfully reset {fixed} books for re-download")
        return fixed
        
    except sqlite3.Error as e:
        print(f"❌ Database error during fix: {e}")
        return 0

def fix_corrupted_files(corrupted_files, dry_run=False):
    """Remove corrupted files and reset download status."""
    if not corrupted_files:
        return 0
    
    print(f"\n🔧 {'Would fix' if dry_run else 'Fixing'} {len(corrupted_files)} corrupted files...")
    
    fixed = 0
    for item in corrupted_files:
        asin = item['asin']
        filepath = item['file']
        
        if dry_run:
            print(f"   Would delete: {filepath}")
            print(f"   Would reset ASIN: {asin}")
            fixed += 1
            continue
        
        # Remove corrupted file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"   🗑️  Deleted corrupted file: {os.path.basename(filepath)}")
            else:
                print(f"   ⚠️  File already missing: {os.path.basename(filepath)}")
        except OSError as e:
            print(f"   ❌ Error deleting {filepath}: {e}")
            continue
        
        # Reset download status
        try:
            con = sqlite3.connect(config + "/audiobooks.db")
            cur = con.cursor()
            cur.execute('UPDATE audiobooks SET downloaded = 0 WHERE asin = ?', [asin])
            con.commit()
            con.close()
            
            book_info_con = sqlite3.connect(config + "/audiobooks.db")
            book_info_cur = book_info_con.cursor()
            book_info = book_info_cur.execute('SELECT title, authors FROM audiobooks WHERE asin = ?', [asin]).fetchone()
            book_info_con.close()
            
            if book_info:
                print(f"   ✅ Reset for re-download: {book_info[0]} by {book_info[1]}")
                fixed += 1
                
        except sqlite3.Error as e:
            print(f"   ❌ Error resetting download status for ASIN {asin}: {e}")
    
    if not dry_run:
        print(f"✅ Successfully fixed {fixed} corrupted files")
    
    return fixed

def remove_orphaned_files(orphaned_files, dry_run=False):
    """Remove orphaned files that aren't tracked in the database."""
    if not orphaned_files:
        return 0
    
    print(f"\n🔧 {'Would remove' if dry_run else 'Removing'} {len(orphaned_files)} orphaned files...")
    
    removed = 0
    for item in orphaned_files:
        filepath = item['file']
        asin = item['asin']
        size_mb = item['size'] / (1024 * 1024)
        
        if dry_run:
            print(f"   Would delete: {filepath} ({size_mb:.1f} MB, ASIN: {asin})")
            removed += 1
            continue
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"   🗑️  Deleted: {os.path.basename(filepath)} ({size_mb:.1f} MB)")
                removed += 1
            else:
                print(f"   ⚠️  File already missing: {os.path.basename(filepath)}")
        except OSError as e:
            print(f"   ❌ Error deleting {filepath}: {e}")
    
    if not dry_run:
        print(f"✅ Successfully removed {removed} orphaned files")
    
    return removed

def main():
    parser = argparse.ArgumentParser(description='Verify audiobook database and file integrity')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick check (skip ffprobe verification)')
    parser.add_argument('--orphans-only', action='store_true', help='Only check for orphaned files')
    parser.add_argument('--fix', '-f', action='store_true', help='Automatically fix issues found')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    args = parser.parse_args()
    
    print("🔍 Audiobook Integrity Verification Tool")
    print("=" * 50)
    
    # Connect to database
    try:
        con = sqlite3.connect(config + "/audiobooks.db")
        cur = con.cursor()
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)
    
    # Check for orphaned files
    orphaned = []
    if args.orphans_only or args.verbose:
        print("\n📂 Scanning for orphaned files...")
        orphaned = scan_orphaned_files()
        if orphaned:
            print(f"⚠️  Found {len(orphaned)} orphaned files:")
            for item in orphaned:
                size_mb = item['size'] / (1024 * 1024)
                print(f"   - {item['file']} (ASIN: {item['asin']}, {size_mb:.1f} MB)")
        else:
            print("✅ No orphaned files found")
        
        if args.orphans_only:
            con.close()
            return
    
    # Get all books from database
    try:
        books = cur.execute('''
            SELECT asin, title, subtitle, authors, series_title, narrators, 
                   series_sequence, release_date, downloaded 
            FROM audiobooks 
            ORDER BY authors, series_sequence, title
        ''').fetchall()
    except sqlite3.Error as e:
        print(f"❌ Error querying database: {e}")
        con.close()
        sys.exit(1)
    
    print(f"\n📚 Verifying {len(books)} books from database...")
    
    stats = {
        'total': len(books),
        'downloaded': 0,
        'files_found': 0,
        'files_verified': 0,
        'corrupted': 0,
        'missing': 0,
        'not_downloaded': 0
    }
    
    issues = []
    missing_asins = []
    corrupted_files = []
    
    for book in books:
        asin, title, subtitle, authors, series_title, narrators, series_sequence, release_date, downloaded = book
        
        if downloaded == 0:
            stats['not_downloaded'] += 1
            if args.verbose:
                print(f"📋 {title} by {authors} (ASIN: {asin}) - Not downloaded")
            continue
        
        stats['downloaded'] += 1
        
        # Generate expected path
        expected_path = create_audiobook_path(authors, title, series_title, subtitle, narrators, series_sequence, release_date)
        
        # Find actual files
        files = find_audiobook_files(expected_path if use_folders else audiobook_directory, asin)
        
        if not files:
            stats['missing'] += 1
            missing_asins.append(asin)
            issues.append({
                'type': 'missing',
                'book': f"{title} by {authors}",
                'asin': asin,
                'expected_path': expected_path
            })
            if args.verbose:
                print(f"❌ {title} by {authors} (ASIN: {asin}) - File not found")
            continue
        
        stats['files_found'] += 1
        
        if args.verbose:
            print(f"📁 {title} by {authors} (ASIN: {asin}) - Found {len(files)} file(s)")
        
        # Verify file integrity (unless quick mode)
        if not args.quick:
            for filepath in files:
                integrity = verify_file_integrity(filepath)
                
                if integrity['valid']:
                    stats['files_verified'] += 1
                    if args.verbose:
                        duration_hours = integrity['duration'] / 3600
                        size_mb = integrity['size'] / (1024 * 1024)
                        print(f"   ✅ {os.path.basename(filepath)} - {duration_hours:.1f}h, {size_mb:.1f}MB")
                else:
                    stats['corrupted'] += 1
                    corrupted_files.append({
                        'asin': asin,
                        'file': filepath,
                        'book': f"{title} by {authors}"
                    })
                    issues.append({
                        'type': 'corrupted',
                        'book': f"{title} by {authors}",
                        'asin': asin,
                        'file': filepath,
                        'error': integrity.get('error', 'Unknown error')
                    })
                    if args.verbose:
                        print(f"   ❌ {os.path.basename(filepath)} - CORRUPTED: {integrity.get('error', 'Unknown')}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"Total books in database: {stats['total']}")
    print(f"Marked as downloaded: {stats['downloaded']}")
    print(f"Not downloaded: {stats['not_downloaded']}")
    print(f"Files found: {stats['files_found']}")
    
    if not args.quick:
        print(f"Files verified: {stats['files_verified']}")
        print(f"Corrupted files: {stats['corrupted']}")
    
    print(f"Missing files: {stats['missing']}")
    
    # Print issues
    if issues:
        print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            if issue['type'] == 'missing':
                print(f"   📋 MISSING: {issue['book']} (ASIN: {issue['asin']})")
                if args.verbose:
                    print(f"      Expected at: {issue['expected_path']}")
            elif issue['type'] == 'corrupted':
                print(f"   🔥 CORRUPTED: {issue['book']} (ASIN: {issue['asin']})")
                print(f"      File: {issue['file']}")
                print(f"      Error: {issue['error']}")
    else:
        print("\n✅ No issues found!")
    
    # Apply fixes if requested
    if (args.fix or args.dry_run) and (missing_asins or corrupted_files or orphaned):
        print("\n" + "=" * 50)
        print(f"🔧 {'DRY RUN - PROPOSED FIXES' if args.dry_run else 'APPLYING FIXES'}")
        print("=" * 50)
        
        total_fixed = 0
        
        # Fix missing files
        if missing_asins:
            total_fixed += fix_missing_files(missing_asins, args.dry_run)
        
        # Fix corrupted files
        if corrupted_files:
            total_fixed += fix_corrupted_files(corrupted_files, args.dry_run)
        
        # Remove orphaned files (only if explicitly requested)
        if orphaned and args.verbose and len(orphaned) > 0:
            response = input(f"\n❓ Found {len(orphaned)} orphaned files. Remove them? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                total_fixed += remove_orphaned_files(orphaned, args.dry_run)
        
        if args.dry_run:
            print(f"\n📋 DRY RUN SUMMARY: Would fix {total_fixed} issues")
            print("   Use --fix to actually apply these changes")
        else:
            print(f"\n✅ FIXES COMPLETE: Successfully fixed {total_fixed} issues")
            if total_fixed > 0:
                print("   Fixed books will be re-downloaded on the next cycle")
    
    elif issues and not args.fix and not args.dry_run:
        print(f"\n💡 TIP: Use --fix to automatically resolve these issues")
        print("        Use --dry-run --fix to see what would be changed first")
    
    con.close()

if __name__ == "__main__":
    main()