"""
User Session Handler module for managing user session data across the application.
Provides a simple container to store and access user session data.
"""
import logging

class SessionHandler:
    """
    Handles user session management.
    Provides access to current user data during the application session.
    """
    
    def __init__(self):
        """Initialize the session handler."""
        self.user_data = None
        self.logger = logging.getLogger('main')
        
    def set_user_data(self, user_data):
        """
        Set the current user data.
        
        Args:
            user_data: Dictionary containing user information
        """
        try:
            self.user_data = dict(user_data) if user_data else None
            self.logger.debug(f"Session: User data set for {self.get_username()}")
        except Exception as e:
            self.logger.error(f"Error setting user data: {e}")
            self.user_data = None
            
    def get_user_data(self):
        """
        Get all user data.
        
        Returns:
            Dictionary containing all user data or None if not logged in
        """
        return self.user_data
    
    def clear_session(self):
        """Clear the current session."""
        self.logger.debug(f"Session: Cleared for user {self.get_username()}")
        self.user_data = None
        
    def is_logged_in(self):
        """
        Check if a user is currently logged in.
        
        Returns:
            True if a user is logged in, False otherwise
        """
        return self.user_data is not None
        
    def get_user_id(self):
        """
        Get the current user ID.
        
        Returns:
            Current user ID or None if not logged in
        """
        if self.user_data:
            return self.user_data.get('id')
        return None
        
    def get_username(self):
        """
        Get the current username.
        
        Returns:
            Current username or None if not logged in
        """
        if self.user_data:
            return self.user_data.get('username')
        return None
        
    def get_fullname(self):
        """
        Get the current user's full name.
        
        Returns:
            Current user's full name or None if not logged in
        """
        if self.user_data:
            return self.user_data.get('fullname')
        return None
        
    def get_email(self):
        """
        Get the current user's email.
        
        Returns:
            Current user's email or None if not logged in
        """
        if self.user_data:
            return self.user_data.get('email')
        return None
        
    def get_role(self):
        """
        Get the current user's role.
        
        Returns:
            Current user's role or None if not logged in
        """
        if self.user_data:
            return self.user_data.get('role', '').lower()
        return None
        
    def is_admin(self):
        """
        Check if the current user is an admin.
        
        Returns:
            True if the user is an admin, False otherwise
        """
        if self.user_data:
            return self.user_data.get('role', '').lower() == 'admin'
        return False

# Create a single instance to be used throughout the application
session = SessionHandler()