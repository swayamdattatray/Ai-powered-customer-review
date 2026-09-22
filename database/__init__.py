"""
Database package init exposing DatabaseManager and helper legacy functions.
"""

from database.db_manager import DatabaseManager

_default_db = DatabaseManager()

def get_connection():
    return _default_db.get_connection()

def create_database():
    _default_db.init_database()

def add_review(*args, **kwargs):
    return _default_db.add_review(*args, **kwargs)

__all__ = ["DatabaseManager", "get_connection", "create_database", "add_review"]
