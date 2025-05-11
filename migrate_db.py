import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./logbook.db"  # Default to SQLite if not specified

# Create engine
engine = create_engine(DATABASE_URL)

def migrate_database():
    """Add new columns to the logbook_entries table if they don't exist.
    If there are issues, backup the database and recreate the schema.
    """
    try:
        print("Starting database migration...")
        
        # For SQLite databases
        if 'sqlite' in DATABASE_URL:
            db_path = DATABASE_URL.replace('sqlite:///', '')
            if db_path.startswith('./'):
                db_path = db_path[2:]
                
            # Create a backup of the database before making changes
            if os.path.exists(db_path):
                backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"Creating backup of database at {backup_path}")
                shutil.copy2(db_path, backup_path)
            
            # Try to alter the table first
            try:
                with engine.connect() as connection:
                    # Check existing columns
                    result = connection.execute(text("PRAGMA table_info(logbook_entries)"))
                    columns = [row[1] for row in result]
                    
                    # Add task column if it doesn't exist
                    if 'task' not in columns:
                        print("Adding 'task' column to logbook_entries table...")
                        connection.execute(text("ALTER TABLE logbook_entries ADD COLUMN task VARCHAR(255)"))
                        print("Column 'task' added successfully!")
                    else:
                        print("Column 'task' already exists. Skipping.")
                    
                    # Add resolution_time column if it doesn't exist
                    if 'resolution_time' not in columns:
                        print("Adding 'resolution_time' column to logbook_entries table...")
                        connection.execute(text("ALTER TABLE logbook_entries ADD COLUMN resolution_time TIMESTAMP"))
                        print("Column 'resolution_time' added successfully!")
                    else:
                        print("Column 'resolution_time' already exists. Skipping.")
            except Exception as e:
                print(f"Error altering table: {e}")
                print("Attempting to recreate the table with the new schema...")
                
                # If altering fails, recreate the table with the new schema
                # This is a more drastic approach but ensures the schema is correct
                with engine.connect() as connection:
                    # Get existing data
                    try:
                        result = connection.execute(text("SELECT * FROM logbook_entries"))
                        rows = result.fetchall()
                        column_names = result.keys()
                        print(f"Retrieved {len(rows)} rows from logbook_entries")
                        
                        # Create a temporary table with the new schema
                        connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS logbook_entries_new (
                            id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            start_date DATE NOT NULL,
                            end_date DATE,
                            responsible_person TEXT NOT NULL,
                            location_id INTEGER NOT NULL,
                            device TEXT NOT NULL,
                            task TEXT,
                            call_description TEXT NOT NULL,
                            solution_description TEXT,
                            resolution_time TIMESTAMP,
                            status TEXT NOT NULL,
                            downtime_hours REAL,
                            category_id INTEGER,
                            priority TEXT,
                            created_at TIMESTAMP,
                            updated_at TIMESTAMP,
                            completed_by_id TEXT,
                            is_deleted BOOLEAN DEFAULT 0
                        )
                        """))
                        
                        # Copy data to the new table
                        for row in rows:
                            # Convert row to dict
                            row_dict = dict(zip(column_names, row))
                            
                            # Prepare columns and values for INSERT
                            columns = []
                            placeholders = []
                            values = []
                            
                            for col, val in row_dict.items():
                                if col != 'resolution_time':  # Skip the new column
                                    columns.append(col)
                                    placeholders.append('?')
                                    values.append(val)
                            
                            # Add resolution_time with NULL value
                            columns.append('resolution_time')
                            placeholders.append('NULL')
                            
                            # Build and execute INSERT statement
                            insert_sql = f"INSERT INTO logbook_entries_new ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                            connection.execute(text(insert_sql), values)
                        
                        # Replace the old table with the new one
                        connection.execute(text("DROP TABLE logbook_entries"))
                        connection.execute(text("ALTER TABLE logbook_entries_new RENAME TO logbook_entries"))
                        print("Table recreated successfully with the new schema!")
                    except Exception as inner_e:
                        print(f"Error recreating table: {inner_e}")
                        print("Please restore from the backup and try again.")
        
        # For PostgreSQL
        elif 'postgresql' in DATABASE_URL:
            with engine.connect() as connection:
                # Check task column
                result = connection.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'logbook_entries' AND column_name = 'task'"
                ))
                if not result.fetchone():
                    print("Adding 'task' column to logbook_entries table...")
                    connection.execute(text("ALTER TABLE logbook_entries ADD COLUMN task VARCHAR(255)"))
                    print("Column 'task' added successfully!")
                else:
                    print("Column 'task' already exists. Skipping.")
                
                # Check resolution_time column
                result = connection.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'logbook_entries' AND column_name = 'resolution_time'"
                ))
                if not result.fetchone():
                    print("Adding 'resolution_time' column to logbook_entries table...")
                    connection.execute(text("ALTER TABLE logbook_entries ADD COLUMN resolution_time TIMESTAMP"))
                    print("Column 'resolution_time' added successfully!")
                else:
                    print("Column 'resolution_time' already exists. Skipping.")
        
        # For other databases (MySQL, etc.)
        else:
            print("Unsupported database type. Please modify this script for your database.")
            return
        
        print("Database migration completed successfully!")
    
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_database()
