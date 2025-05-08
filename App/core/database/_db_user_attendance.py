"""
Database Operations for User Attendance

This module provides functions for managing user attendance records in the database.
"""
import sqlite3
import datetime
import json
import os
import logging
import time
from pathlib import Path
from App.core.user._user_session_handler import session


class UserAttendanceDB:
    """
    Class to handle all database operations related to user attendance.
    """
    
    def __init__(self):
        """Initialize the database connection using config."""
        self.logger = logging.getLogger('main')
        self.config = self._load_config()
        self.db_path = self._get_db_path()
        self.conn = None
    
    def _load_config(self):
        """Load application configuration from config.json."""
        try:
            # Get the absolute path to the config file
            base_dir = str(Path(__file__).parents[3])  # Go up 3 levels from this file
            config_path = os.path.join(base_dir, 'App', 'config', 'config.json')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config in UserAttendanceDB: {e}")
            raise ValueError(f"Failed to load config file: {e}")
    
    def _get_db_path(self):
        """Get database path from config."""
        # Get database path directly from config
        db_path = self.config['database']['path']
        
        # Convert to absolute path if it's relative
        if not os.path.isabs(db_path):
            base_dir = str(Path(__file__).parents[3])  # Go up 3 levels from this file
            db_path = os.path.join(base_dir, db_path)
        
        return db_path
    
    def _connect_db(self):
        """Connect to the SQLite database with retry logic."""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Make sure the database path exists
                db_dir = os.path.dirname(self.db_path)
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    
                # Check if the database file exists and is accessible
                if not os.path.exists(self.db_path):
                    self.logger.error(f"Database file does not exist: {self.db_path}")
                    return False
                
                # Check if journal file exists and database might be locked
                journal_path = self.db_path + "-journal"
                if os.path.exists(journal_path):
                    self.logger.warning(f"Journal file exists, database might be in use: {journal_path}")
                
                # Try to connect with increased timeout to handle locks
                self.conn = sqlite3.connect(self.db_path, timeout=30)
                self.conn.row_factory = sqlite3.Row  # Use dictionary-like rows
                
                # Set journal mode to WAL for better concurrency
                cursor = self.conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA busy_timeout=10000;")  # 10 second busy timeout
                
                # Test the connection with a simple query
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                return True
            except sqlite3.Error as e:
                attempt += 1
                self.logger.error(f"Database connection error (attempt {attempt}/{max_attempts}): {e}")
                # Make sure conn is None if connection failed
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass
                self.conn = None
                
                if attempt < max_attempts:
                    # Wait before retrying (exponential backoff)
                    time.sleep(1 * attempt)
                else:
                    self.logger.error("Maximum connection attempts reached, giving up")
                    return False
            except Exception as e:
                self.logger.error(f"Unexpected error connecting to database: {e}")
                # Make sure conn is None if connection failed
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass
                self.conn = None
                return False
        
        return False
    
    def _close_db(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def verify_attendance_pin(self, pin):
        """
        Verify if the entered PIN matches the stored PIN for the current user.
        
        Args:
            pin (str): The PIN entered by the user
            
        Returns:
            bool: True if PIN is correct, False otherwise
        """
        if not session.is_logged_in():
            self.logger.warning("Attempted to verify PIN when not logged in")
            return False
        
        user_id = session.get_user_id()
        if not user_id:
            self.logger.warning("No user ID found in session")
            return False
        
        try:
            if not self._connect_db():
                return False
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT attendance_pin FROM users WHERE id = ?", 
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                self.logger.warning(f"No user found with ID {user_id}")
                return False
            
            stored_pin = result['attendance_pin']
            
            # If no PIN is set in the database
            if not stored_pin:
                self.logger.warning(f"User with ID {user_id} has no attendance PIN set")
                return False
            
            return pin == stored_pin
        
        except sqlite3.Error as e:
            self.logger.error(f"Database error during PIN verification: {e}")
            return False
        finally:
            self._close_db()
    
    def check_in(self):
        """
        Record a check-in event for the current user.
        Always creates a new attendance record for each check-in.
        
        Returns:
            bool: True if check-in was successful, False otherwise
        """
        if not session.is_logged_in():
            self.logger.warning("Attempted to check in when not logged in")
            return False
        
        user_id = session.get_user_id()
        if not user_id:
            self.logger.warning("No user ID found in session")
            return False
        
        # Use a dedicated connection for this transaction
        conn = None
        try:
            # Create direct connection to database
            db_path = self.db_path
            conn = sqlite3.connect(db_path, timeout=60)
            conn.row_factory = sqlite3.Row
            
            # Get current date and time
            now = datetime.datetime.now()
            current_date = now.date()
            check_in_time = now.time().strftime("%H:%M:%S")
            check_in_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Always create a new attendance record for each check-in
            cursor = conn.cursor()
            
            # First, check if there's any unclosed record using this connection
            cursor.execute(
                "SELECT id FROM user_attendance "
                "WHERE user_id = ? AND check_in_time IS NOT NULL AND check_out_time IS NULL "
                "ORDER BY full_date DESC, check_in_time DESC LIMIT 1",
                (user_id,)
            )
            unclosed_record = cursor.fetchone()
            
            if unclosed_record:
                self.logger.warning(f"User {user_id} attempted to check in but has an unclosed check-in record")
                return False
                
            cursor.execute(
                "INSERT INTO user_attendance "
                "(user_id, full_date, year, month, day, check_in_time, check_in_datetime, status, is_present, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                (
                    user_id,
                    current_date,
                    now.year,
                    now.month,
                    now.day,
                    check_in_time,
                    check_in_datetime,
                    "Present",  # Default status
                    1,  # is_present = True
                )
            )
                
            conn.commit()
            
            # Get the ID of the newly created record
            attendance_id = cursor.lastrowid
            
            self.logger.info(f"User {user_id} checked in at {check_in_time} (Record ID: {attendance_id})")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error during check-in: {e}")
            # Try to rollback if there's a connection and transaction
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during check-in: {e}")
            # Try to rollback if there's a connection and transaction
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False
        finally:
            if conn:
                conn.close()
    
    def check_out(self):
        """
        Record a check-out event for the current user.
        Updates the most recent unclosed check-in record for the user, regardless of date.
        
        Returns:
            bool: True if check-out was successful, False otherwise
        """
        if not session.is_logged_in():
            self.logger.warning("Attempted to check out when not logged in")
            return False
        
        user_id = session.get_user_id()
        if not user_id:
            self.logger.warning("No user ID found in session")
            return False
        
        # Use a dedicated connection for this transaction
        conn = None
        try:
            # Create direct connection to database
            db_path = self.db_path
            conn = sqlite3.connect(db_path, timeout=60)
            conn.row_factory = sqlite3.Row
            
            # Get current date and time
            now = datetime.datetime.now()
            check_out_time = now.time().strftime("%H:%M:%S")
            check_out_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Find the most recent check-in record that doesn't have a check-out time
            # regardless of date (to handle overnight shifts or forgot to check out)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, full_date, check_in_time, check_in_datetime FROM user_attendance "
                "WHERE user_id = ? AND check_in_time IS NOT NULL AND check_out_time IS NULL "
                "ORDER BY full_date DESC, check_in_time DESC LIMIT 1",
                (user_id,)
            )
            existing_record_row = cursor.fetchone()
            
            if not existing_record_row:
                # No open check-in record found, can't check out
                self.logger.warning(f"User {user_id} attempted to check out but has no open check-in record")
                return False
            
            # Convert sqlite3.Row to dict to properly use .get() method
            existing_record = dict(existing_record_row)
            
            # Calculate working hours
            working_hours = None
            
            # If we have the full datetime field, use that for precise calculation
            if 'check_in_datetime' in existing_record and existing_record['check_in_datetime']:
                check_in_dt = datetime.datetime.strptime(existing_record['check_in_datetime'], "%Y-%m-%d %H:%M:%S")
                check_out_dt = now
                
                # Calculate hours as decimal, properly handling multi-day spans
                delta = check_out_dt - check_in_dt
                working_hours = delta.total_seconds() / 3600  # Convert to hours
            else:
                # Fallback to the old method if check_in_datetime is not available
                # Get the check-in date and time
                check_in_date = existing_record['full_date']
                check_in_time = existing_record['check_in_time']
                
                # Create datetime objects for check-in and check-out
                if isinstance(check_in_date, str):
                    check_in_date = datetime.datetime.strptime(check_in_date, "%Y-%m-%d").date()
                
                check_in_time = datetime.datetime.strptime(check_in_time, "%H:%M:%S").time()
                check_in_dt = datetime.datetime.combine(check_in_date, check_in_time)
                
                check_out_dt = datetime.datetime.combine(now.date(), datetime.datetime.strptime(check_out_time, "%H:%M:%S").time())
                
                # Calculate the difference, handling multi-day spans
                if check_out_dt < check_in_dt:
                    days_diff = (now.date() - check_in_date).days
                    if days_diff <= 0:
                        # If same day but checkout time is earlier, assume next day
                        check_out_dt += datetime.timedelta(days=1)
                    else:
                        # Otherwise use the actual date
                        check_out_dt = datetime.datetime.combine(now.date(), datetime.datetime.strptime(check_out_time, "%H:%M:%S").time())
                
                # Calculate hours as decimal
                delta = check_out_dt - check_in_dt
                working_hours = delta.total_seconds() / 3600  # Convert to hours
            
            # Update the existing record with check-out time
            cursor.execute(
                "UPDATE user_attendance SET check_out_time = ?, check_out_datetime = ?, working_hours = ?, "
                "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (check_out_time, check_out_datetime, working_hours, existing_record['id'])
            )
                
            conn.commit()
            
            self.logger.info(f"User {user_id} checked out at {check_out_time} (Record ID: {existing_record['id']})")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error during check-out: {e}")
            # Try to rollback if there's a connection and transaction
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during check-out: {e}")
            # Try to rollback if there's a connection and transaction
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False
        finally:
            if conn:
                conn.close()
    
    def get_today_attendance(self, user_id=None):
        """
        Get all attendance records for today for a specific user.
        
        Args:
            user_id (int, optional): User ID to get attendance for. Defaults to logged-in user.
            
        Returns:
            list: List of attendance records for today
        """
        if user_id is None:
            if not session.is_logged_in():
                self.logger.warning("Attempted to get attendance when not logged in")
                return []
            
            user_id = session.get_user_id()
            if not user_id:
                self.logger.warning("No user ID found in session")
                return []
        
        try:
            if not self._connect_db():
                return []
            
            # Get current date
            current_date = datetime.date.today()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM user_attendance "
                "WHERE user_id = ? AND full_date = ? "
                "ORDER BY check_in_time DESC",
                (user_id, current_date)
            )
            results = cursor.fetchall()
            
            # Convert rows to dicts
            return [dict(row) for row in results]
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting today's attendance: {e}")
            return []
        finally:
            self._close_db()
    
    def get_latest_attendance_record(self, user_id=None):
        """
        Get the most recent attendance record for a user.
        This is useful for determining if a user is checked in or out.
        
        Args:
            user_id (int, optional): User ID to get attendance for. Defaults to logged-in user.
            
        Returns:
            dict: The most recent attendance record or None if not found
        """
        if user_id is None:
            if not session.is_logged_in():
                self.logger.warning("Attempted to get attendance when not logged in")
                return None
            
            user_id = session.get_user_id()
            if not user_id:
                self.logger.warning("No user ID found in session")
                return None
        
        try:
            if not self._connect_db():
                return None
            
            # Get current date
            current_date = datetime.date.today()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM user_attendance "
                "WHERE user_id = ? AND full_date = ? "
                "ORDER BY check_in_time DESC LIMIT 1",
                (user_id, current_date)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert row to dict
            return dict(result)
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting latest attendance record: {e}")
            return None
        finally:
            self._close_db()
    
    def get_attendance_history(self, user_id=None, limit=30, offset=0):
        """
        Get attendance history for a user.
        
        Args:
            user_id (int, optional): User ID to get attendance for. Defaults to logged-in user.
            limit (int, optional): Maximum number of records to return. Defaults to 30.
            offset (int, optional): Number of records to skip. Defaults to 0.
            
        Returns:
            list: List of attendance records
        """
        if user_id is None:
            if not session.is_logged_in():
                self.logger.warning("Attempted to get attendance history when not logged in")
                return []
            
            user_id = session.get_user_id()
            if not user_id:
                self.logger.warning("No user ID found in session")
                return []
        
        try:
            if not self._connect_db():
                return []
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM user_attendance "
                "WHERE user_id = ? "
                "ORDER BY full_date DESC "
                "LIMIT ? OFFSET ?",
                (user_id, limit, offset)
            )
            results = cursor.fetchall()
            
            # Convert rows to dicts
            return [dict(row) for row in results]
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting attendance history: {e}")
            return []
        finally:
            self._close_db()
    
    def get_last_check_in_time(self, user_id=None):
        """
        Get the most recent check-in time for a user (from any date).
        
        Args:
            user_id (int, optional): User ID to get check-in time for. Defaults to logged-in user.
            
        Returns:
            dict: The most recent check-in record or None if not found
        """
        if user_id is None:
            if not session.is_logged_in():
                self.logger.warning("Attempted to get last check-in when not logged in")
                return None
            
            user_id = session.get_user_id()
            if not user_id:
                self.logger.warning("No user ID found in session")
                return None
        
        try:
            if not self._connect_db():
                return None
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM user_attendance "
                "WHERE user_id = ? AND check_in_time IS NOT NULL "
                "ORDER BY full_date DESC, check_in_time DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert row to dict
            return dict(result)
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting last check-in time: {e}")
            return None
        finally:
            self._close_db()
    
    def get_last_check_out_time(self, user_id=None):
        """
        Get the most recent check-out time for a user (from any date).
        
        Args:
            user_id (int, optional): User ID to get check-out time for. Defaults to logged-in user.
            
        Returns:
            dict: The most recent check-out record or None if not found
        """
        if user_id is None:
            if not session.is_logged_in():
                self.logger.warning("Attempted to get last check-out when not logged in")
                return None
            
            user_id = session.get_user_id()
            if not user_id:
                self.logger.warning("No user ID found in session")
                return None
        
        try:
            if not self._connect_db():
                return None
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM user_attendance "
                "WHERE user_id = ? AND check_out_time IS NOT NULL "
                "ORDER BY full_date DESC, check_out_time DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert row to dict
            return dict(result)
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting last check-out time: {e}")
            return None
        finally:
            self._close_db()
    
    def get_unclosed_attendance_record(self, user_id=None):
        """
        Get the most recent attendance record with no check-out time for a user, regardless of date.
        This is important to prevent users from checking in again when they haven't checked out
        from a previous day.
        
        Args:
            user_id (int, optional): User ID to check. Defaults to logged-in user.
            
        Returns:
            dict: The most recent unclosed attendance record or None if not found
        """
        if user_id is None:
            if not session.is_logged_in():
                self.logger.warning("Attempted to get unclosed attendance record when not logged in")
                return None
            
            user_id = session.get_user_id()
            if not user_id:
                self.logger.warning("No user ID found in session")
                return None
        
        try:
            if not self._connect_db():
                return None
            
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM user_attendance "
                "WHERE user_id = ? AND check_in_time IS NOT NULL AND check_out_time IS NULL "
                "ORDER BY full_date DESC, check_in_time DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert row to dict
            return dict(result)
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting unclosed attendance record: {e}")
            return None
        finally:
            self._close_db()

# Create a global instance for easy import
attendance_db = UserAttendanceDB()