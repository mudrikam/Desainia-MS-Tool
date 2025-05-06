"""
User Authentication module for handling login, registration and user management.
Uses SQLite database for storing user data.
"""
import os
import sqlite3
import hashlib
import datetime
import json
import logging
from pathlib import Path

class UserAuth:
    """
    Handles user authentication, registration, and profile management.
    Uses database.db for storing user data.
    """
    
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.current_user = None
        self.conn = None
        self.logger = logging.getLogger('main')
        
        # Initialize settings with defaults
        self.settings = {
            "allow_registration": True,
            "allow_password_reset": True,
            "remember_login": False,
            "session_timeout_minutes": 60
        }
        
        # Get database path
        if self.app and hasattr(self.app, 'BASE_DIR'):
            self.base_dir = self.app.BASE_DIR
            self.config = self.app.BASE_DIR.config
            self.db_path = self._get_db_path_from_config()
        else:
            # Fallback if app instance not provided
            self.base_dir = self._get_base_dir()
            self.db_path = self._get_db_path_from_config()
        
        # Load settings and check for existing login
        self._connect_db()
        self._load_settings()
        self._load_current_user()
        self._close_db()

    def _get_base_dir(self):
        """Fallback method to get base directory if app instance is not provided."""
        # Simple helper class to mimic BASE_DIR.get_path
        class PathHelper:
            def __init__(self, base_dir):
                self.base_dir = base_dir
                self.config = self._load_config()
            
            def get_path(self, *paths):
                return os.path.join(self.base_dir, *paths)
                
            def _load_config(self):
                config_path = os.path.join(self.base_dir, 'App', 'config', 'config.json')
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    return {}
        
        # Get project root directory (3 levels up from this file)
        base_dir = str(Path(__file__).parents[3])
        return PathHelper(base_dir)
    
    def _get_db_path_from_config(self):
        """Get database path from config.json"""
        try:
            # Get database path from config
            if hasattr(self, 'config'):
                db_relative_path = self.config.get('database', {}).get('path', 'App/database/database.db')
            elif hasattr(self.base_dir, 'config'):
                db_relative_path = self.base_dir.config.get('database', {}).get('path', 'App/database/database.db')
            else:
                # Load config directly if not available
                config_path = os.path.join(self.base_dir.get_path('App', 'config'), 'config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        db_relative_path = config.get('database', {}).get('path', 'App/database/database.db')
                else:
                    db_relative_path = 'App/database/database.db'
            
            # Convert relative path to absolute
            if not os.path.isabs(db_relative_path):
                if hasattr(self.base_dir, 'get_path'):
                    return self.base_dir.get_path(db_relative_path)
                else:
                    return os.path.join(self.base_dir, db_relative_path)
            return db_relative_path
            
        except Exception as e:
            self.logger.error(f"Error getting database path from config: {e}")
            # Default path if config can't be loaded
            return os.path.join(self.base_dir.get_path('App', 'database'), 'database.db')
    
    def _connect_db(self):
        """Connect to the SQLite database."""
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row  # Use dictionary-like rows
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            return False
    
    def _close_db(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _load_settings(self):
        """Load settings from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT key, value FROM app_settings")
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    key = row['key']
                    value = row['value']
                    
                    # Convert string values to appropriate types
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    
                    self.settings[key] = value
                
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error loading settings: {e}")
            return False

    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_current_user(self):
        """Load current user from database if remember_login is enabled"""
        # Only load user if remember_login is true, otherwise always start logged out
        if not self.settings.get("remember_login", False):
            self.current_user = None
            return
        
        try:
            # Get most recent active session
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT us.user_id, u.* FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.expires_at > datetime('now')
            ORDER BY us.created_at DESC
            LIMIT 1
            """)
            
            user_row = cursor.fetchone()
            if user_row:
                # Convert row to dict for current_user
                self.current_user = dict(user_row)
            else:
                self.current_user = None
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error loading current user: {e}")
            self.current_user = None
    
    def authenticate(self, username, password):
        """Authenticate user and update last login"""
        try:
            if not self._connect_db():
                return None
            
            cursor = self.conn.cursor()
            
            # First, get user by username only
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            
            if not user_row:
                self.logger.info(f"Authentication failed: Username '{username}' not found")
                return None
            
            # Hash the provided password
            hashed_password = self._hash_password(password)
            
            # Get the stored password
            stored_password = user_row['password']
            
            # Check if passwords match (either hashed or direct match for legacy passwords)
            password_match = False
            
            if hashed_password == stored_password:
                # Password matches the stored hash
                password_match = True
            elif password == stored_password:
                # Legacy case: Password is stored in plaintext
                password_match = True
                
                # Update to hashed password for security
                cursor.execute("""
                UPDATE users SET password = ? WHERE id = ?
                """, (hashed_password, user_row['id']))
                self.logger.info(f"Updated legacy password to hashed format for user: {username}")
            
            if not password_match:
                self.logger.info(f"Authentication failed: Invalid password for user '{username}'")
                return None
            
            # Update last login time
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
            UPDATE users SET last_login = ? WHERE id = ?
            """, (now, user_row['id']))
            
            # Create a session if remember_login is enabled
            if self.settings.get("remember_login", False):
                # Generate a session token
                session_token = hashlib.sha256(f"{username}{now}{os.urandom(16).hex()}".encode()).hexdigest()
                
                # Calculate expiry (current time + session_timeout_minutes)
                timeout_minutes = self.settings.get("session_timeout_minutes", 60)
                expires_at = (datetime.datetime.now() + datetime.timedelta(minutes=timeout_minutes)).isoformat()
                
                # Delete any existing sessions for this user
                cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_row['id'],))
                
                # Create new session
                cursor.execute("""
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
                """, (user_row['id'], session_token, expires_at))
            
            # Store user in memory for this session
            self.current_user = dict(user_row)
                
            self.conn.commit()
            return dict(user_row)
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error during authentication: {e}")
            return None
        finally:
            self._close_db()

    def logout(self):
        """Log out current user"""
        try:
            if not self._connect_db():
                return False
            
            # Clear the current user in memory
            if self.current_user:
                cursor = self.conn.cursor()
                
                # Delete any active sessions for this user
                cursor.execute("""
                DELETE FROM user_sessions WHERE user_id = ?
                """, (self.current_user['id'],))
                
                self.conn.commit()
            
            self.current_user = None
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error during logout: {e}")
            return False
        finally:
            self._close_db()
        
    def get_current_user(self):
        """Get current logged in user"""
        # If current_user is not set, try to load it from database
        if self.current_user is None and self.settings.get("remember_login", False):
            if not self._connect_db():
                return None
                
            self._load_current_user()
            self._close_db()
            
        return self.current_user
    
    def register(self, username, password, fullname, email):
        """
        Register a new user
        Returns True if successful, False if username already exists
        """
        try:
            if not self._connect_db():
                return False, "Database connection error"
                
            # Check if registration is allowed
            if not self.settings.get("allow_registration", True):
                return False, "Registration is currently disabled"
            
            cursor = self.conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username already exists"
                
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "Email already in use"
            
            # Hash the password
            hashed_password = self._hash_password(password)
            
            # Insert new user
            cursor.execute("""
            INSERT INTO users (username, password, fullname, email, role)
            VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_password, fullname, email, "user"))
            
            # Get the inserted user
            user_id = cursor.lastrowid
            
            # Create default preferences for the user
            cursor.execute("""
            INSERT INTO user_preferences (user_id, theme, language)
            VALUES (?, ?, ?)
            """, (user_id, "system", "en"))
            
            self.conn.commit()
            
            # Load the newly created user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            new_user = cursor.fetchone()
            
            if new_user:
                # Set as current user
                self.current_user = dict(new_user)
                return True, "Registration successful"
            else:
                return False, "User registration failed"
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error during registration: {e}")
            return False, f"Registration error"
        finally:
            self._close_db()
    
    def reset_password(self, email, new_password, confirm_password):
        """Reset password for user by email"""
        # Check if passwords match
        if new_password != confirm_password:
            return False, "Passwords do not match"
            
        try:
            if not self._connect_db():
                return False, "Database connection error"
                
            # Check if password reset is allowed
            if not self.settings.get("allow_password_reset", True):
                return False, "Password reset is currently disabled"
            
            cursor = self.conn.cursor()
            
            # Find user by email
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                return False, "Email not found"
            
            # Hash the new password
            hashed_password = self._hash_password(new_password)
            
            # Update password
            cursor.execute("""
            UPDATE users SET password = ? WHERE id = ?
            """, (hashed_password, user['id']))
            
            self.conn.commit()
            return True, "Password reset successful"
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error during password reset: {e}")
            return False, "Password reset failed"
        finally:
            self._close_db()
    
    def update_profile(self, username, **kwargs):
        """Update user profile data"""
        try:
            if not self._connect_db():
                return False, "Database connection error"
                
            cursor = self.conn.cursor()
            
            # Find user by username
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            # Build update query dynamically based on provided fields
            allowed_fields = ['fullname', 'email', 'password']
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    # Hash password if it's being updated
                    if key == 'password':
                        value = self._hash_password(value)
                    
                    updates.append(f"{key} = ?")
                    values.append(value)
            
            if not updates:
                return False, "No valid fields to update"
            
            # Add user ID to values
            values.append(user['id'])
            
            # Execute update query
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            
            # If current user is being updated, reload it
            if self.current_user and self.current_user['id'] == user['id']:
                cursor.execute("SELECT * FROM users WHERE id = ?", (user['id'],))
                updated_user = cursor.fetchone()
                if updated_user:
                    self.current_user = dict(updated_user)
            
            self.conn.commit()
            return True, "Profile updated successfully"
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error during profile update: {e}")
            return False, "Profile update failed"
        finally:
            self._close_db()
    
    def update_settings(self, **kwargs):
        """Update application settings"""
        try:
            if not self._connect_db():
                return False, "Database connection error"
                
            cursor = self.conn.cursor()
            
            # Update settings in memory and database
            for key, value in kwargs.items():
                if key in self.settings:
                    # Update in memory
                    self.settings[key] = value
                    
                    # Update in database
                    cursor.execute("""
                    UPDATE app_settings SET value = ?, updated_at = datetime('now')
                    WHERE key = ?
                    """, (str(value), key))
            
            self.conn.commit()
            return True, "Settings updated successfully"
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error during settings update: {e}")
            return False, "Settings update failed"
        finally:
            self._close_db()
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            if not self._connect_db():
                return None
                
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                return dict(user)
            else:
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting user: {e}")
            return None
        finally:
            self._close_db()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            if not self._connect_db():
                return None
                
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user:
                return dict(user)
            else:
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting user: {e}")
            return None
        finally:
            self._close_db()
    
    def get_all_users(self):
        """Get all users (admin function)"""
        try:
            if not self._connect_db():
                return []
                
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, username, fullname, email, role, created_at, last_login FROM users")
            users = cursor.fetchall()
            
            # Convert rows to dictionaries
            return [dict(user) for user in users]
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting users: {e}")
            return []
        finally:
            self._close_db()
