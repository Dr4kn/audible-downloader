"""
Database operations module for the audiobook downloader.
Handles all SQLite database interactions and schema management.
"""

import sqlite3
import sys
from typing import List, Optional, Tuple
from config import DATABASE_PATH


class AudiobookDatabase:
    """Manages the audiobook database operations."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and create tables."""
        self.connection = sqlite3.connect(self.db_path)
        with self.connection:
            self._create_tables()
            self._migrate_schema()
    
    def _create_tables(self):
        """Create the audiobooks table if it doesn't exist."""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS audiobooks (
                asin TEXT UNIQUE,
                title TEXT NOT NULL,
                subtitle TEXT,
                authors TEXT NOT NULL,
                series_title TEXT,
                narrators TEXT,
                series_sequence INT,
                release_date TEXT,
                downloaded INT,
                is_downloadable INT DEFAULT 1,
                restriction_reason TEXT,
                last_download_attempt TEXT
            )
        """)
    
    def _migrate_schema(self):
        """Add new columns if they don't exist (for backward compatibility)."""
        migrations = [
            ("is_downloadable", "INT DEFAULT 1"),
            ("restriction_reason", "TEXT"),
            ("last_download_attempt", "TEXT")
        ]
        
        for column_name, column_def in migrations:
            try:
                self.connection.execute(f"ALTER TABLE audiobooks ADD COLUMN {column_name} {column_def}")
            except sqlite3.OperationalError:
                pass  # Column already exists
    
    def add_book(self, book_data: dict) -> bool:
        """Add a new book to the database if it doesn't exist."""
        try:
            values = [
                book_data.get('asin', ''),
                book_data.get('title', ''),
                book_data.get('subtitle', ''),
                book_data.get('authors', ''),
                book_data.get('series_title', ''),
                book_data.get('narrators', ''),
                book_data.get('series_sequence', None),
                book_data.get('release_date', ''),
                0,  # downloaded
                1,  # is_downloadable (default)
                None,  # restriction_reason
                None   # last_download_attempt
            ]
            
            cursor = self.connection.cursor()
            existing = cursor.execute('SELECT * FROM audiobooks WHERE asin=?', [book_data.get('asin', '')]).fetchone()
            
            if existing is None:
                cursor.execute('INSERT INTO audiobooks VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
                self.connection.commit()
                return True
            return False
        except Exception as e:
            print(f"Error adding book to database: {e}")
            sys.stdout.flush()
            return False
    
    def get_unchecked_books(self) -> List[Tuple[str, str]]:
        """Get books that haven't been checked for downloadability."""
        cursor = self.connection.cursor()
        return cursor.execute('''
            SELECT asin, title FROM audiobooks 
            WHERE is_downloadable = 1 AND restriction_reason IS NULL 
            AND downloaded = 0
            ORDER BY asin
        ''').fetchall()
    
    def get_downloadable_books(self) -> List[Tuple[str, str, str]]:
        """Get books that are downloadable and not yet downloaded."""
        cursor = self.connection.cursor()
        return cursor.execute('''
            SELECT asin, title, restriction_reason 
            FROM audiobooks 
            WHERE downloaded = 0 AND is_downloadable = 1
        ''').fetchall()
    
    def get_restricted_books(self) -> List[Tuple[str, str, str]]:
        """Get books that are restricted from downloading."""
        cursor = self.connection.cursor()
        return cursor.execute('''
            SELECT asin, title, restriction_reason 
            FROM audiobooks 
            WHERE downloaded = 0 AND is_downloadable = 0
        ''').fetchall()
    
    def update_downloadability(self, asin: str, is_downloadable: bool, reason: Optional[str] = None):
        """Update the downloadability status of a book."""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE audiobooks 
            SET is_downloadable = ?, restriction_reason = ?
            WHERE asin = ?
        ''', (1 if is_downloadable else 0, reason, asin))
        self.connection.commit()
    
    def update_download_attempt(self, asin: str, timestamp: str):
        """Update the last download attempt timestamp."""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE audiobooks 
            SET last_download_attempt = ? 
            WHERE asin = ?
        ''', (timestamp, asin))
        self.connection.commit()
    
    def mark_downloaded(self, asin: str):
        """Mark a book as successfully downloaded."""
        cursor = self.connection.cursor()
        cursor.execute('UPDATE audiobooks SET downloaded = 1 WHERE asin = ?', (asin,))
        self.connection.commit()
    
    def get_book_info(self, asin: str) -> Optional[Tuple]:
        """Get book information by ASIN."""
        cursor = self.connection.cursor()
        return cursor.execute('SELECT title FROM audiobooks WHERE asin=?', (asin,)).fetchone()
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()


# Global database instance
db = AudiobookDatabase()