"""
Database compatibility layer

This module provides a compatibility layer for code that might still 
be expecting an SQLAlchemy db object. The app has transitioned to
using file-based storage instead of SQLAlchemy.
"""

class DummyDB:
    """
    A dummy class that mimics the essential methods of SQLAlchemy's db object
    but doesn't actually do anything with a database.
    """
    def create_all(self):
        """Dummy method to maintain compatibility"""
        pass
    
    def drop_all(self):
        """Dummy method to maintain compatibility"""
        pass
    
    def session(self):
        """Dummy method to maintain compatibility"""
        return self

    def commit(self):
        """Dummy method to maintain compatibility"""
        pass
    
    def rollback(self):
        """Dummy method to maintain compatibility"""
        pass
    
    def close(self):
        """Dummy method to maintain compatibility"""
        pass

# Create a singleton instance
db = DummyDB() 