"""
Database Migration Module

This module handles database creation and migrations using SQLite.
It will be run at application startup to ensure the database is properly set up.
"""
import os
import sqlite3
import json
import logging
import hashlib
from pathlib import Path

class DatabaseMigration:
    """
    Handles SQLite database creation and migrations.
    """
    
    def __init__(self, app_instance=None):
        """
        Initialize the database migration handler.
        
        Args:
            app_instance: The application instance with BASE_DIR attribute
        """
        self.app = app_instance
        self.logger = logging.getLogger('main')  # Use main logger instead of separate one
        
        # Get database path from config
        if self.app and hasattr(self.app, 'BASE_DIR'):
            self.base_dir = self.app.BASE_DIR
            self.config = self.app.BASE_DIR.config
        else:
            # Fallback if app instance not provided
            self.base_dir = self._get_base_dir()
            self.config = self._load_config()
        
        # Get database path from config or use default
        self.db_path = self.config.get('database', {}).get('path', 
            os.path.join(self.base_dir.get_path('App', 'database'), 'database.db'))
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Database connection
        self.conn = None
    
    def _get_base_dir(self):
        """Fallback method to get base directory if app instance is not provided."""
        # Simple helper class to mimic BASE_DIR.get_path
        class PathHelper:
            def __init__(self, base_dir):
                self.base_dir = base_dir
            
            def get_path(self, *paths):
                return os.path.join(self.base_dir, *paths)
        
        # Get project root directory (3 levels up from this file)
        base_dir = str(Path(__file__).parents[3])
        return PathHelper(base_dir)
    
    def _load_config(self):
        """Fallback method to load config if app instance is not provided."""
        config_path = os.path.join(self.base_dir.get_path('App', 'config'), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def _connect_db(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Use dictionary-like rows
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return False
    
    def _close_db(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _table_exists(self, table_name):
        """Check if a table exists in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error checking if table {table_name} exists: {e}")
            return False
    
    def _create_tables(self):
        """Create all necessary database tables with complete schema."""
        try:
            cursor = self.conn.cursor()
            
            # Create users table with all required fields
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                fullname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                address TEXT,
                birth_date DATE,
                gender TEXT,
                start_date DATE,
                department TEXT,
                bank_name TEXT,
                bank_account_number TEXT,
                bank_account_holder TEXT,
                role TEXT NOT NULL,
                attendance_pin TEXT,
                profile_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            """)
            
            # Create user_preferences table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                theme TEXT,
                language TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            # Create files table for tracking uploaded files
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_path TEXT,
                file_type TEXT,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            # Create app_settings table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create user_sessions table for remember login feature
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            # Create departments table to store department data
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create user_attendance table for tracking employee attendance
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_date DATE NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                check_in_time TIME,
                check_out_time TIME,
                working_hours FLOAT,
                status TEXT NOT NULL,
                is_present BOOLEAN DEFAULT 0,
                is_absent BOOLEAN DEFAULT 0, 
                is_sick BOOLEAN DEFAULT 0,
                is_permission BOOLEAN DEFAULT 0,
                is_late BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            # Create attendance_status table for tracking attendance statuses
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error creating tables: {e}")
            return False
    
    def _ensure_default_admin(self):
        """Create default admin user if no users exist"""
        try:
            cursor = self.conn.cursor()
            
            # Check if users table is empty
            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()['count'] == 0:
                # Create default admin user with hashed password
                hashed_password = hashlib.sha256("admin".encode()).hexdigest()
                
                cursor.execute("""
                INSERT INTO users (username, password, fullname, email, role)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    "admin",
                    hashed_password,
                    "Default Administrator",
                    "admin@example.com",
                    "admin"
                ))
                
                # Get user ID
                user_id = cursor.lastrowid
                
                # Create default preferences for admin
                cursor.execute("""
                INSERT INTO user_preferences (user_id, theme, language)
                VALUES (?, ?, ?)
                """, (user_id, "system", "en"))
                
                self.conn.commit()
                
                self.logger.info("Created default admin user")
            
            return True
        except Exception as e:
            self.logger.error(f"Error creating default admin: {e}")
            return False
    
    def run_migrations(self):
        """Run database migrations to create tables and initialize data if needed."""
        if not self._connect_db():
            return False
        
        try:
            db_exists = os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0
            
            # Get list of existing tables in the database
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = set(row['name'] for row in cursor.fetchall())
            
            # List of all tables that should exist in the current schema
            required_tables = {
                'users', 'user_preferences', 'files', 'app_settings', 
                'user_sessions', 'departments', 'user_attendance', 'attendance_status'
            }
            
            # Check if all required tables exist
            missing_tables = required_tables - existing_tables
            
            if missing_tables:
                self.logger.info(f"Database exists but missing tables: {', '.join(missing_tables)}")
                self.logger.info("Creating missing tables...")
                
                # Create all tables - _create_tables handles "IF NOT EXISTS" so it won't
                # recreate tables that already exist
                if not self._create_tables():
                    return False
                
                # Only initialize default data for newly created tables
                # This avoids duplicating default data in existing tables
                self._initialize_missing_tables(missing_tables)
                
                return "updated"  # Indicate that the database was updated
            else:
                # All tables exist, just ensure they're up to date
                if not self._create_tables():
                    return False
                
                # Create default admin user if needed
                if not self._ensure_default_admin():
                    self.logger.error("Failed to create default admin user")
            
            return "exists" if db_exists else "created"
        
        finally:
            self._close_db()
            
    def _initialize_missing_tables(self, missing_tables):
        """Initialize default data only for newly created tables."""
        try:
            cursor = self.conn.cursor()
            
            # Initialize default app settings if app_settings was missing
            if 'app_settings' in missing_tables:
                default_settings = {
                    "allow_registration": "True",
                    "allow_password_reset": "True",
                    "remember_login": "False",
                    "session_timeout_minutes": "60"
                }
                
                for key, value in default_settings.items():
                    cursor.execute("""
                    INSERT INTO app_settings (key, value)
                    VALUES (?, ?)
                    """, (key, value))
            
            # Initialize default departments if departments was missing
            if 'departments' in missing_tables:
                default_departments = [
                    ("Management", "Company management and executives"),
                    ("HR", "Human Resources department"),
                    ("IT", "Information Technology department"),
                    ("Finance", "Finance and accounting department"),
                    ("Marketing", "Marketing and communications department"),
                    ("Operations", "Operations and logistics department"),
                    ("Sales", "Sales and customer relations department"),
                    ("R&D", "Research and development department")
                ]
                
                for dept_name, dept_desc in default_departments:
                    cursor.execute("""
                    INSERT INTO departments (name, description)
                    VALUES (?, ?)
                    """, (dept_name, dept_desc))
            
            # Initialize default attendance statuses if attendance_status was missing
            if 'attendance_status' in missing_tables:
                default_statuses = [
                    ("Present", "Employee was present for work", "#4CAF50", 1),
                    ("Absent", "Employee was absent without notification", "#F44336", 0),
                    ("Sick", "Employee was absent due to illness", "#FF9800", 0),
                    ("Permission", "Employee was absent with permission", "#2196F3", 0),
                    ("Late", "Employee arrived late", "#FFC107", 0),
                    ("No Information", "No attendance information available", "#757575", 0)
                ]
                
                for status_name, status_desc, status_color, is_default in default_statuses:
                    cursor.execute("""
                    INSERT INTO attendance_status (name, description, color, is_default)
                    VALUES (?, ?, ?, ?)
                    """, (status_name, status_desc, status_color, is_default))
            
            
            # Add initialization for other tables if needed
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error initializing missing tables: {e}")
            return False

def run():
    """
    Run database migrations. This function can be called directly
    from the application's startup code.
    """
    migration = DatabaseMigration()
    return migration.run_migrations()

if __name__ == "__main__":
    # Run migrations when script is executed directly
    run()