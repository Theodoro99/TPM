#!/usr/bin/env python
"""
Tests for database operations
"""
import sys
import os
import unittest
from datetime import datetime, date
import uuid

# Add the project directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LogbookEntry, Location, StatusEnum, PriorityEnum


class TestDatabase(unittest.TestCase):
    """Test cases for database operations"""
    
    def setUp(self):
        """Set up test database session"""
        self.session = SessionLocal()
    
    def tearDown(self):
        """Clean up after tests"""
        self.session.close()
    
    def test_connection(self):
        """Test that we can connect to the database"""
        # If this doesn't raise an exception, the connection is working
        self.session.execute("SELECT 1")
    
    def test_location_query(self):
        """Test that we can query locations from the database"""
        # This test assumes there's at least one location in the database
        # If not, it will fail, which is expected in a test environment
        locations = self.session.query(Location).all()
        
        # Just check if we can retrieve locations, not testing specific data
        self.assertIsNotNone(locations)
    
    def test_entry_query(self):
        """Test that we can query logbook entries"""
        # Get all entries - this just tests the query functionality
        entries = self.session.query(LogbookEntry).all()
        
        # We don't assert on the number of entries since it may vary
        # Just checking that the query executes without errors
        self.assertIsNotNone(entries)


if __name__ == "__main__":
    unittest.main()
