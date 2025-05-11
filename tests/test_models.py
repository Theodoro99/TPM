#!/usr/bin/env python
"""
Basic tests for database models
"""
import sys
import os
import unittest
from datetime import datetime, date

# Add the project directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.models import LogbookEntry, User, Location, StatusEnum, PriorityEnum, RoleEnum


class TestModels(unittest.TestCase):
    """Test cases for database models"""

    def test_logbook_entry_creation(self):
        """Test that a LogbookEntry can be created with valid data"""
        entry = LogbookEntry(
            id="550e8400-e29b-41d4-a716-446655440000",
            user_id="550e8400-e29b-41d4-a716-446655440001",
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 2),
            responsible_person="Test Person",
            location_id=1,
            device="Test Device",
            task="Test Task",
            call_description="Test Description",
            solution_description="Test Solution",
            status=StatusEnum.OPEN,
            priority=PriorityEnum.MEDIUM
        )
        
        self.assertEqual(str(entry.id), "550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(entry.responsible_person, "Test Person")
        self.assertEqual(entry.device, "Test Device")
        self.assertEqual(entry.status, StatusEnum.OPEN)
        self.assertEqual(entry.priority, PriorityEnum.MEDIUM)
    
    def test_user_creation(self):
        """Test that a User can be created with valid data"""
        user = User(
            id="550e8400-e29b-41d4-a716-446655440002",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            role=RoleEnum.TECHNICIAN
        )
        
        self.assertEqual(str(user.id), "550e8400-e29b-41d4-a716-446655440002")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, RoleEnum.TECHNICIAN)
    
    def test_status_enum(self):
        """Test that StatusEnum has the expected values"""
        self.assertEqual(StatusEnum.OPEN.value, "open")
        self.assertEqual(StatusEnum.ONGOING.value, "ongoing")
        self.assertEqual(StatusEnum.COMPLETED.value, "completed")
        self.assertEqual(StatusEnum.ESCALATION.value, "escalation")
    
    def test_priority_enum(self):
        """Test that PriorityEnum has the expected values"""
        self.assertEqual(PriorityEnum.LOW.value, "low")
        self.assertEqual(PriorityEnum.MEDIUM.value, "medium")
        self.assertEqual(PriorityEnum.HIGH.value, "high")


if __name__ == "__main__":
    unittest.main()
