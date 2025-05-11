import sys
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Add the project directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.models import LogbookEntry, StatusEnum, PriorityEnum, Location
from app.db.database import SessionLocal

def add_test_entry_with_resolution_time():
    # Use the existing SessionLocal from the app
    session = SessionLocal()
    
    try:
        # Create a test entry with a specific resolution time
        created_at = datetime.now() - timedelta(days=1)  # Yesterday
        resolution_time = created_at + timedelta(hours=2, minutes=30)  # 2.5 hours after creation
        
        # First, we need to create or get a location since location_id is an Integer, not UUID
        # Check if we have any locations in the database
        location = session.query(Location).first()
        
        if not location:
            # Create a new location if none exists
            location = Location(
                name="Test Location",
                description="Test location for resolution time testing",
                is_active=True,
                created_at=datetime.now()
            )
            session.add(location)
            session.flush()  # This will assign an ID to the location
        
        # Create the entry with proper types
        test_entry = LogbookEntry(
            id=uuid.uuid4(),  # SQLAlchemy will convert this to string for SQLite
            user_id=uuid.uuid4(),
            start_date=created_at.date(),
            end_date=datetime.now().date(),
            responsible_person="Test Technician",
            location_id=location.id,  # Use the integer ID from the location
            device="Test Device",
            task="Testing",
            call_description="Test entry with resolution time",
            solution_description="This is a test entry to verify resolution time display",
            resolution_time=resolution_time,
            status=StatusEnum.COMPLETED,
            priority=PriorityEnum.MEDIUM,
            created_at=created_at,
            updated_at=datetime.now()
        )
        
        # Add and commit to the database
        session.add(test_entry)
        session.commit()
        
        print(f"Test entry added with resolution time: {resolution_time}")
        print(f"Resolution time is {(resolution_time - created_at).total_seconds() / 3600:.2f} hours after creation")
        
    except Exception as e:
        print(f"Error adding test entry: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_test_entry_with_resolution_time()
