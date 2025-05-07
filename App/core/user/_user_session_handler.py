"""
User Session Handler module for managing user session data across the application.
Provides a simple container to store and access user session data.
"""
import logging

class UserSessionHandler:
    """
    Singleton class to handle user session data across the application.
    This class provides a centralized location to store and retrieve
    user session information that can be accessed by any component.
    """
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSessionHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Session data
        self._user_data = None
        self._initialized = True
        self.logger = logging.getLogger('main')
    
    def set_user_data(self, user_data):
        """
        Set the current user data
        
        Args:
            user_data (dict): User data dictionary or None to clear the session
        """
        self._user_data = user_data
        self.logger.info(f"Session user data set: {self.get_username()}")
    
    def clear_session(self):
        """Clear the current user session"""
        username = self.get_username()
        self._user_data = None
        self.logger.info(f"Session cleared for user: {username}")
        return True
    
    def get_user_data(self):
        """Get the current user data"""
        return self._user_data
    
    def is_logged_in(self):
        """Check if a user is currently logged in"""
        return self._user_data is not None
    
    def get_user_id(self):
        """Get the current user ID"""
        if self._user_data and 'id' in self._user_data:
            return self._user_data['id']
        return None
    
    def get_username(self):
        """Get the current username"""
        if self._user_data and 'username' in self._user_data:
            return self._user_data['username']
        return None
    
    def get_fullname(self):
        """Get the current user's full name"""
        if self._user_data and 'fullname' in self._user_data:
            return self._user_data['fullname']
        return None
    
    def get_email(self):
        """Get the current user's email"""
        if self._user_data and 'email' in self._user_data:
            return self._user_data['email']
        return None
    
    def get_role(self):
        """Get the current user's role"""
        if self._user_data and 'role' in self._user_data:
            return self._user_data['role']
        return None
    
    def is_admin(self):
        """Check if the current user is an admin"""
        return self.get_role() == 'admin'

# Create a global instance that can be imported anywhere
session = UserSessionHandler()