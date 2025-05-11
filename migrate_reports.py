import os
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
    """Add the report-related tables to the database."""
    try:
        print("Starting report tables migration...")
        
        # For SQLite
        if 'sqlite' in DATABASE_URL:
            with engine.connect() as connection:
                # Check if report_templates table exists
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='report_templates'"))
                if not result.fetchone():
                    print("Creating report_templates table...")
                    connection.execute(text("""
                        CREATE TABLE report_templates (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(100) NOT NULL UNIQUE,
                            description TEXT,
                            template_type VARCHAR(50) NOT NULL,
                            config JSON,
                            created_by_id VARCHAR(36) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            is_active BOOLEAN DEFAULT 1,
                            FOREIGN KEY (created_by_id) REFERENCES users(id)
                        )
                    """))
                    print("report_templates table created successfully!")
                else:
                    print("report_templates table already exists. Skipping.")
                
                # Check if reports table exists
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'"))
                if not result.fetchone():
                    print("Creating reports table...")
                    connection.execute(text("""
                        CREATE TABLE reports (
                            id VARCHAR(36) PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            template_id INTEGER,
                            parameters JSON,
                            start_date DATE,
                            end_date DATE,
                            file_path VARCHAR(255),
                            file_type VARCHAR(20),
                            status VARCHAR(20) DEFAULT 'generated',
                            created_by_id VARCHAR(36) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (template_id) REFERENCES report_templates(id),
                            FOREIGN KEY (created_by_id) REFERENCES users(id)
                        )
                    """))
                    print("reports table created successfully!")
                else:
                    print("reports table already exists. Skipping.")
                
                # Check if report_schedules table exists
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='report_schedules'"))
                if not result.fetchone():
                    print("Creating report_schedules table...")
                    connection.execute(text("""
                        CREATE TABLE report_schedules (
                            id INTEGER PRIMARY KEY,
                            report_id VARCHAR(36) NOT NULL,
                            frequency VARCHAR(20) NOT NULL,
                            day_of_week INTEGER,
                            day_of_month INTEGER,
                            time_of_day VARCHAR(5),
                            recipients JSON,
                            is_active BOOLEAN DEFAULT 1,
                            last_run TIMESTAMP,
                            next_run TIMESTAMP,
                            created_by_id VARCHAR(36) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (report_id) REFERENCES reports(id),
                            FOREIGN KEY (created_by_id) REFERENCES users(id)
                        )
                    """))
                    print("report_schedules table created successfully!")
                else:
                    print("report_schedules table already exists. Skipping.")
        
        # For PostgreSQL
        elif 'postgresql' in DATABASE_URL:
            with engine.connect() as connection:
                # Check if report_templates table exists
                result = connection.execute(text(
                    "SELECT to_regclass('public.report_templates')"
                ))
                if not result.fetchone()[0]:
                    print("Creating report_templates table...")
                    connection.execute(text("""
                        CREATE TABLE report_templates (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(100) NOT NULL UNIQUE,
                            description TEXT,
                            template_type VARCHAR(50) NOT NULL,
                            config JSONB,
                            created_by_id UUID NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            is_active BOOLEAN DEFAULT TRUE,
                            FOREIGN KEY (created_by_id) REFERENCES users(id)
                        )
                    """))
                    print("report_templates table created successfully!")
                else:
                    print("report_templates table already exists. Skipping.")
                
                # Check if reports table exists
                result = connection.execute(text(
                    "SELECT to_regclass('public.reports')"
                ))
                if not result.fetchone()[0]:
                    print("Creating reports table...")
                    connection.execute(text("""
                        CREATE TABLE reports (
                            id UUID PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            template_id INTEGER,
                            parameters JSONB,
                            start_date DATE,
                            end_date DATE,
                            file_path VARCHAR(255),
                            file_type VARCHAR(20),
                            status VARCHAR(20) DEFAULT 'generated',
                            created_by_id UUID NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (template_id) REFERENCES report_templates(id),
                            FOREIGN KEY (created_by_id) REFERENCES users(id)
                        )
                    """))
                    print("reports table created successfully!")
                else:
                    print("reports table already exists. Skipping.")
                
                # Check if report_schedules table exists
                result = connection.execute(text(
                    "SELECT to_regclass('public.report_schedules')"
                ))
                if not result.fetchone()[0]:
                    print("Creating report_schedules table...")
                    connection.execute(text("""
                        CREATE TABLE report_schedules (
                            id SERIAL PRIMARY KEY,
                            report_id UUID NOT NULL,
                            frequency VARCHAR(20) NOT NULL,
                            day_of_week INTEGER,
                            day_of_month INTEGER,
                            time_of_day VARCHAR(5),
                            recipients JSONB,
                            is_active BOOLEAN DEFAULT TRUE,
                            last_run TIMESTAMP,
                            next_run TIMESTAMP,
                            created_by_id UUID NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (report_id) REFERENCES reports(id),
                            FOREIGN KEY (created_by_id) REFERENCES users(id)
                        )
                    """))
                    print("report_schedules table created successfully!")
                else:
                    print("report_schedules table already exists. Skipping.")
        
        # For other databases (MySQL, etc.)
        else:
            print("Unsupported database type. Please modify this script for your database.")
            return
        
        print("Report tables migration completed successfully!")
    
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_database()
