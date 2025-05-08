"""
Database operations for user dashboard functionality.

This module provides functions to retrieve user data for the dashboard.
"""
import sqlite3
import json
import os
import logging
from pathlib import Path
import shutil
from PIL import Image

class UserDashboardDB:
    """
    Handles database operations for the user dashboard.
    Retrieves user profile data and other related information.
    """
    
    def __init__(self, app_instance=None):
        """
        Initialize database connection for user dashboard operations.
        
        Args:
            app_instance: The application instance with BASE_DIR attribute
        """
        self.app = app_instance
        self.logger = logging.getLogger('main')
        self.conn = None
        
        # Get base directory
        if self.app and hasattr(self.app, 'BASE_DIR'):
            self.base_dir = self.app.BASE_DIR
        else:
            # Fallback for base directory if app instance not provided
            self.base_dir = self._get_base_dir()
            
        # Always load config from config.json
        self.config = self._load_config()
        
        # Get database path strictly from config - no default fallback
        # Fix for cross-platform compatibility: normalize path separators
        db_path = self.config['database']['path']
        # Convert any Windows backslashes to forward slashes for cross-platform compatibility
        db_path = db_path.replace('\\', '/')
        
        # Ensure it's an absolute path by joining with base directory
        if not os.path.isabs(db_path):
            self.db_path = os.path.normpath(os.path.join(self.base_dir.get_path(''), db_path))
        else:
            self.db_path = os.path.normpath(db_path)
                
        # Profile images directory
        self.profile_images_dir = os.path.join(
            self.base_dir.get_path('UserData'), 
            'profile_images'
        )
            
        # Ensure profile images directory exists
        os.makedirs(self.profile_images_dir, exist_ok=True)
    
    def _get_base_dir(self):
        """Fallback method to get base directory if app instance is not provided."""
        # Simple helper class to mimic BASE_DIR.get_path
        class PathHelper:
            def __init__(self, base_dir):
                self.base_dir = base_dir
            
            def get_path(self, *paths):
                return os.path.join(self.base_dir, *paths)
        
        # Get project root directory (3 levels up from this file)
        base_dir = str(Path(__file__).parents[2])
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
            # Print DB path for debugging
            print(f"UserDashboardDB connecting to database: {self.db_path}")
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Use dictionary-like rows
            
            print(f"UserDashboardDB database connection successful: {self.db_path}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            print(f"UserDashboardDB database connection failed: {self.db_path}")
            print(f"Error: {e}")
            return False
    
    def _close_db(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_user_data(self, username, no_cache=False, include_profile=True):
        """
        Get full user data for the dashboard.
        
        Args:
            username: Username to fetch data for
            no_cache: If True, always fetch fresh data from database
            include_profile: If True, include all profile fields (address, phone, etc.)
            
        Returns:
            Dictionary containing user data or None if not found
        """
        if not self._connect_db():
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # Basic query to get user data including preferences
            if not include_profile:
                cursor.execute("""
                    SELECT 
                        u.id, u.username, u.fullname, u.email, u.role,
                        u.created_at, u.last_login, u.profile_image,
                        up.theme, up.language
                    FROM users u
                    LEFT JOIN user_preferences up ON u.id = up.user_id
                    WHERE u.username = ?
                """, (username,))
            else:
                # Enhanced query to get ALL user profile fields 
                cursor.execute("""
                    SELECT 
                        u.id, u.username, u.fullname, u.email, u.role,
                        u.created_at, u.last_login, u.profile_image,
                        up.theme, up.language,
                        u.phone_number, u.address, u.gender, u.department,
                        u.birth_date, u.start_date, u.bank_name, 
                        u.bank_account_number, u.bank_account_holder
                    FROM users u
                    LEFT JOIN user_preferences up ON u.id = up.user_id
                    WHERE u.username = ?
                """, (username,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Convert to dict for easier handling
                user_dict = dict(user_data)
                # Log all retrieved fields for debugging
                self.logger.debug(f"Retrieved user data fields: {list(user_dict.keys())}")
                return user_dict
            
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching user data: {e}")
            return None
        finally:
            self._close_db()
    
    def get_app_name(self):
        """
        Get application name from config.json.
        
        Returns:
            Application name string or default value
        """
        try:
            if not self.config:
                self.config = self._load_config()
            
            return self.config.get('application', {}).get('name', 'Desainia Rak Arsip')
        except Exception as e:
            self.logger.error(f"Error getting application name: {e}")
            return 'Desainia Rak Arsip'
            
    def save_profile_image(self, username, image_path):
        """
        Save a profile image for a user.
        
        Args:
            username: Username to set profile image for
            image_path: Path to the image file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image file does not exist: {image_path}")
            return False
            
        try:
            # Get user ID
            user_data = self.get_user_data(username)
            if not user_data:
                self.logger.error(f"User not found: {username}")
                return False
                
            user_id = user_data.get('id')
            
            # Create user specific folder
            user_profile_dir = os.path.join(self.profile_images_dir, str(user_id))
            os.makedirs(user_profile_dir, exist_ok=True)
            
            # Process and resize the image
            try:
                # Open the image
                with Image.open(image_path) as img:
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Calculate new size while preserving aspect ratio
                    width, height = img.size
                    max_size = 200  # Set maximum size for the image
                    
                    if width > height:
                        new_width = max_size
                        new_height = int(height * (max_size / width))
                    else:
                        new_height = max_size
                        new_width = int(width * (max_size / height))
                    
                    # Resize the image
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Save to user profile directory
                    filename = f"profile_{user_id}.jpg"
                    save_path = os.path.join(user_profile_dir, filename)
                    img.save(save_path, "JPEG", quality=85)
            except Exception as e:
                self.logger.error(f"Error processing image: {e}")
                return False
                
            # Update user record in database
            if not self._connect_db():
                return False
                
            try:
                cursor = self.conn.cursor()
                
                # Simpan hanya nama file saja, bukan path lengkap
                profile_image = f"{user_id}/profile_{user_id}.jpg"
                
                # Update user profile_image field
                cursor.execute("""
                    UPDATE users
                    SET profile_image = ?
                    WHERE id = ?
                """, (profile_image, user_id))
                
                self.conn.commit()
                return True
                
            except sqlite3.Error as e:
                self.logger.error(f"Error updating profile image in database: {e}")
                return False
            finally:
                self._close_db()
                
        except Exception as e:
            self.logger.error(f"Error saving profile image: {e}")
            return False
            
    def get_profile_image_path(self, profile_image):
        """
        Get full path for a profile image.
        
        Args:
            profile_image: Profile image stored in database
            
        Returns:
            Full path to profile image
        """
        if not profile_image:
            return None
            
        return os.path.join(self.profile_images_dir, profile_image)
            
    def delete_profile_image(self, username):
        """
        Delete a user's profile image.
        
        Args:
            username: Username to delete profile image for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user data
            user_data = self.get_user_data(username)
            if not user_data:
                self.logger.error(f"User not found: {username}")
                return False
                
            user_id = user_data.get('id')
            profile_image = user_data.get('profile_image')
            
            # Connect to database
            if not self._connect_db():
                return False
                
            try:
                cursor = self.conn.cursor()
                
                # Set profile_image to NULL
                cursor.execute("""
                    UPDATE users
                    SET profile_image = NULL
                    WHERE id = ?
                """, (user_id,))
                
                self.conn.commit()
                
                # Delete the image file if it exists
                if profile_image and os.path.exists(profile_image):
                    try:
                        os.remove(profile_image)
                    except Exception as e:
                        self.logger.error(f"Error removing profile image file: {e}")
                
                return True
                
            except sqlite3.Error as e:
                self.logger.error(f"Error deleting profile image from database: {e}")
                return False
            finally:
                self._close_db()
                
        except Exception as e:
            self.logger.error(f"Error deleting profile image: {e}")
            return False

    def update_user_info(self, user_id, fullname=None, username=None, email=None, password=None, 
                          phone_number=None, address=None, birth_date=None, gender=None, 
                          start_date=None, department=None, bank_name=None, 
                          bank_account_number=None, bank_account_holder=None):
        """
        Update user information in the database.
        
        Args:
            user_id: User ID to update
            fullname: New full name (or None to keep current)
            username: New username (or None to keep current)
            email: New email (or None to keep current)
            password: New password (or None to keep current)
            phone_number: New phone number (or None to keep current)
            address: New address (or None to keep current)
            birth_date: New birth date (or None to keep current)
            gender: New gender (or None to keep current)
            start_date: New start date (or None to keep current)
            department: New department (or None to keep current)
            bank_name: New bank name (or None to keep current)
            bank_account_number: New bank account number (or None to keep current)
            bank_account_holder: New bank account holder name (or None to keep current)
            
        Returns:
            Tuple (success, message) where success is True if update successful
        """
        if not self._connect_db():
            return False, "Database connection failed"
        
        try:
            cursor = self.conn.cursor()
            
            # Verify the user exists
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                return False, "User not found"
            
            # Start building the update query
            fields_to_update = []
            params = []
            
            if fullname is not None:
                fields_to_update.append("fullname = ?")
                params.append(fullname)
            
            if email is not None:
                # Check if email is already in use by another user
                cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
                if cursor.fetchone():
                    return False, "Email already in use by another user"
                fields_to_update.append("email = ?")
                params.append(email)
            
            if username is not None:
                # Check if username is already in use by another user
                cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
                if cursor.fetchone():
                    return False, "Username already in use by another user"
                fields_to_update.append("username = ?")
                params.append(username)
            
            if password is not None:
                # Hash the password
                import hashlib
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                fields_to_update.append("password = ?")
                params.append(hashed_password)
                
            # Add the new fields to the update query
            if phone_number is not None:
                fields_to_update.append("phone_number = ?")
                params.append(phone_number)
                
            if address is not None:
                fields_to_update.append("address = ?")
                params.append(address)
                
            if birth_date is not None:
                fields_to_update.append("birth_date = ?")
                params.append(birth_date)
                
            if gender is not None:
                fields_to_update.append("gender = ?")
                params.append(gender)
                
            if start_date is not None:
                fields_to_update.append("start_date = ?")
                params.append(start_date)
                
            if department is not None:
                fields_to_update.append("department = ?")
                params.append(department)
                
            # Add bank account fields to the update query
            if bank_name is not None:
                fields_to_update.append("bank_name = ?")
                params.append(bank_name)
                
            if bank_account_number is not None:
                fields_to_update.append("bank_account_number = ?")
                params.append(bank_account_number)
                
            if bank_account_holder is not None:
                fields_to_update.append("bank_account_holder = ?")
                params.append(bank_account_holder)
            
            # If nothing to update, return success
            if not fields_to_update:
                return True, "No changes required"
            
            # Build the complete query
            query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE id = ?"
            params.append(user_id)
            
            # Execute the update
            cursor.execute(query, params)
            self.conn.commit()
            
            return True, "User information updated successfully"
            
        except sqlite3.Error as e:
            self.logger.error(f"Error updating user info: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            self._close_db()

    def get_departments(self):
        """
        Get list of all departments from the departments table.
        
        Returns:
            List of department names or empty list if no departments found
        """
        if not self._connect_db():
            return []
        
        try:
            cursor = self.conn.cursor()
            
            # Query to get all department names
            cursor.execute("SELECT name FROM departments ORDER BY name")
            
            departments = [dept['name'] for dept in cursor.fetchall()]
            return departments
            
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching departments: {e}")
            return []
        finally:
            self._close_db()