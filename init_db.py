import os
from dotenv import load_dotenv
import uuid
from datetime import date, datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

# Import database models and engine
from app.db.database import engine, SessionLocal
from app.db.models import Base, User, LogbookEntry, Location, Category, RoleEnum, StatusEnum, PriorityEnum

# Create password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create database tables
Base.metadata.create_all(bind=engine)

# Function to create initial data
def init_database():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already contains data. Skipping initialization.")
            return
        
        print("Initializing database with sample data...")
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@preventplus.com",
            password_hash=pwd_context.hash("admin"),
            role=RoleEnum.ADMIN,
            full_name="System Administrator",
            department="IT",
            phone_number="+1234567890"
        )
        db.add(admin_user)
        
        # Create technician user
        tech_user = User(
            id=uuid.uuid4(),
            username="technician",
            email="tech@preventplus.com",
            password_hash=pwd_context.hash("technician"),
            role=RoleEnum.TECHNICIAN,
            full_name="John Technician",
            department="Maintenance",
            phone_number="+1987654321"
        )
        db.add(tech_user)
        
        # Create locations
        locations = [
            Location(id=1, name="Production Line 1", description="Building A, 1st Floor", created_by_id=admin_user.id),
            Location(id=2, name="Production Line 2", description="Building A, 1st Floor", created_by_id=admin_user.id),
            Location(id=3, name="Assembly Area", description="Building B, Ground Floor", created_by_id=admin_user.id),
            Location(id=4, name="Packaging Department", description="Building C, 2nd Floor", created_by_id=admin_user.id),
            Location(id=5, name="Quality Control", description="Building B, 3rd Floor", created_by_id=admin_user.id),
        ]
        for location in locations:
            db.add(location)
        
        # Create categories
        categories = [
            Category(id=1, name="Mechanical", description="Mechanical issues and repairs", created_by_id=admin_user.id),
            Category(id=2, name="Electrical", description="Electrical problems and maintenance", created_by_id=admin_user.id),
            Category(id=3, name="Software", description="Software bugs and updates", created_by_id=admin_user.id),
            Category(id=4, name="Network", description="Network connectivity issues", created_by_id=admin_user.id),
            Category(id=5, name="Preventive Maintenance", description="Scheduled maintenance tasks", created_by_id=admin_user.id),
        ]
        for category in categories:
            db.add(category)
        
        # Create sample logbook entries
        today = date.today()
        
        # Completed entries
        for i in range(1, 11):
            entry_date = today - timedelta(days=i*3)
            end_date = entry_date + timedelta(days=1)
            entry = LogbookEntry(
                id=uuid.uuid4(),
                user_id=tech_user.id if i % 2 == 0 else admin_user.id,
                start_date=entry_date,
                end_date=end_date,
                responsible_person="John Technician" if i % 2 == 0 else "System Administrator",
                location_id=((i-1) % 5) + 1,
                device=f"Machine {i}",
                call_description=f"Scheduled maintenance for Machine {i}",
                solution_description=f"Performed regular maintenance, replaced worn parts on Machine {i}",
                status=StatusEnum.COMPLETED,
                downtime_hours=4.5,
                category_id=((i-1) % 5) + 1,
                priority=PriorityEnum.MEDIUM
            )
            db.add(entry)
        
        # Open entries
        for i in range(1, 6):
            entry_date = today - timedelta(days=i)
            entry = LogbookEntry(
                id=uuid.uuid4(),
                user_id=tech_user.id if i % 2 == 0 else admin_user.id,
                start_date=entry_date,
                end_date=None,
                responsible_person="John Technician" if i % 2 == 0 else "System Administrator",
                location_id=i,
                device=f"Equipment {i}",
                call_description=f"Unexpected shutdown of Equipment {i}. Needs investigation.",
                solution_description=None,
                status=StatusEnum.OPEN,
                downtime_hours=i * 2.0,
                category_id=i,
                priority=PriorityEnum.HIGH
            )
            db.add(entry)
        
        # Escalated entries
        for i in range(1, 4):
            entry_date = today - timedelta(days=i*2)
            entry = LogbookEntry(
                id=uuid.uuid4(),
                user_id=tech_user.id,
                start_date=entry_date,
                end_date=None,
                responsible_person="John Technician",
                location_id=i,
                device=f"Critical System {i}",
                call_description=f"Major failure in Critical System {i}. Requires specialist attention.",
                solution_description="Attempted standard repairs but issue persists. Escalating to vendor support.",
                status=StatusEnum.ESCALATION,
                downtime_hours=i * 8.0,
                category_id=i,
                priority=PriorityEnum.HIGH
            )
            db.add(entry)
        
        db.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
