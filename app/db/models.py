import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base

"""Database models for the PreventPlus application.

This module contains all SQLAlchemy ORM models representing the database schema.
Includes models for user management, logbook entries, locations, categories,
attachments, audit logging, and reporting functionality.
"""

class RoleEnum(str, enum.Enum):
    """Enumeration for user roles."""
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"


class StatusEnum(str, enum.Enum):
    """Enumeration for logbook entry statuses."""
    OPEN = "open"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    ESCALATION = "escalation"


class PriorityEnum(str, enum.Enum):
    """Enumeration for logbook entry priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    """User model representing application users.

    Attributes:
        id: UUID primary key
        username: Unique username
        email: Unique email address
        password_hash: Hashed password
        full_name: User's full name
        role: User role (admin/manager/technician)
        department: Department affiliation
        phone_number: Contact number
        is_active: Account active status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp
        failed_attempts: Failed login attempts counter
        reset_token: Password reset token
        token_expiry: Reset token expiration
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.TECHNICIAN)
    department = Column(String(100))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    failed_attempts = Column(Integer, default=0)
    reset_token = Column(String(255))
    token_expiry = Column(DateTime)

    # Relationships
    entries = relationship("LogbookEntry", foreign_keys="LogbookEntry.user_id", back_populates="user")
    completed_entries = relationship("LogbookEntry", foreign_keys="LogbookEntry.completed_by_id", back_populates="completed_by")
    attachments = relationship("Attachment", back_populates="uploaded_by")
    locations = relationship("Location", back_populates="created_by")
    categories = relationship("Category", back_populates="created_by")
    settings = relationship("Setting", back_populates="updated_by")
    audit_logs = relationship("AuditLog", back_populates="user")


class LogbookEntry(Base):
    """Logbook entry model representing maintenance records.

    Attributes:
        id: UUID primary key
        user_id: Creator user reference
        start_date: Entry start date
        end_date: Completion date
        responsible_person: Responsible individual
        location_id: Location reference
        device: Device/equipment involved
        task: Task description
        call_description: Issue description
        solution_description: Resolution details
        resolution_time: Time taken to resolve
        status: Current status (open/ongoing/completed/escalation)
        downtime_hours: Downtime duration
        category_id: Category reference
        priority: Priority level (low/medium/high)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_by_id: User who completed the entry
        is_deleted: Soft delete flag
    """

    __tablename__ = "logbook_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    responsible_person = Column(String(100), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    device = Column(String(100), nullable=False)
    task = Column(String(255))  # New field for task selection
    call_description = Column(Text, nullable=False)
    solution_description = Column(Text)
    resolution_time = Column(DateTime)  # New field for resolution time
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.OPEN)
    downtime_hours = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"))
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="entries", foreign_keys=[user_id])
    completed_by = relationship("User", back_populates="completed_entries", foreign_keys=[completed_by_id])
    location = relationship("Location", back_populates="entries")
    category = relationship("Category", back_populates="entries")
    attachments = relationship("Attachment", back_populates="entry")


class Attachment(Base):
    """Attachment model for logbook entry files.

    Attributes:
        id: UUID primary key
        entry_id: Associated logbook entry
        file_name: Original filename
        file_path: Storage path
        file_type: MIME type
        file_size: File size in bytes
        description: Optional description
        uploaded_by_id: Uploading user reference
        uploaded_at: Upload timestamp
        is_deleted: Soft delete flag
    """

    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(UUID(as_uuid=True), ForeignKey("logbook_entries.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    description = Column(Text)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    entry = relationship("LogbookEntry", back_populates="attachments")
    uploaded_by = relationship("User", back_populates="attachments")


class Location(Base):
    """Location model for equipment/device locations.

    Attributes:
        id: Integer primary key
        name: Unique location name
        description: Location details
        parent_id: Parent location reference
        created_at: Creation timestamp
        updated_at: Last update timestamp
        created_by_id: Creator user reference
        is_active: Active status flag
    """

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("locations.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    entries = relationship("LogbookEntry", back_populates="location")
    created_by = relationship("User", back_populates="locations")
    children = relationship("Location")
    parent = relationship("Location", remote_side=[id], back_populates="children")


class Category(Base):
    """Category model for logbook entry classification.

    Attributes:
        id: Integer primary key
        name: Unique category name
        description: Category details
        color_code: Hex color code for UI
        created_at: Creation timestamp
        updated_at: Last update timestamp
        created_by_id: Creator user reference
        is_active: Active status flag
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    color_code = Column(String(7))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    entries = relationship("LogbookEntry", back_populates="category")
    created_by = relationship("User", back_populates="categories")


class Setting(Base):
    """System settings model for configuration storage.

    Attributes:
        id: Integer primary key
        key: Unique setting key
        value: Setting value
        description: Setting purpose
        is_system: System setting flag
        created_at: Creation timestamp
        updated_at: Last update timestamp
        updated_by_id: Last modifying user
    """

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    updated_by = relationship("User", back_populates="settings")


class AuditLog(Base):
    """Audit log model for tracking system actions.

    Attributes:
        id: UUID primary key
        user_id: Acting user reference
        action: Performed action
        entity_type: Affected entity type
        entity_id: Affected entity ID
        details: Action details (JSON)
        ip_address: Request origin IP
        user_agent: Client user agent
        created_at: Event timestamp
    """

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class ReportTemplate(Base):
    """Report template model for predefined report configurations.

    Attributes:
        id: Integer primary key
        name: Template name
        description: Template purpose
        template_type: Report type classification
        config: JSON configuration
        created_by_id: Creator user reference
        created_at: Creation timestamp
        updated_at: Last update timestamp
        is_active: Active status flag
    """

    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    template_type = Column(String(50), nullable=False)  # e.g., 'activity', 'performance', 'maintenance'
    config = Column(JSON)  # Store chart configurations, sections, etc.
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    created_by = relationship("User")
    reports = relationship("Report", back_populates="template")


class Report(Base):
    """Report model for generated reports.

    Attributes:
        id: UUID primary key
        name: Report name
        template_id: Template reference
        parameters: Filter parameters (JSON)
        start_date: Report period start
        end_date: Report period end
        file_path: Generated file path
        file_type: Output format
        status: Generation status
        created_by_id: Creator user reference
        created_at: Generation timestamp
    """

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    parameters = Column(JSON)  # Store filter parameters
    start_date = Column(Date)
    end_date = Column(Date)
    file_path = Column(String(255))  # Path to generated report file if saved
    file_type = Column(String(20))  # PDF, Excel, CSV, etc.
    status = Column(String(20), default="generated")  # draft, generated, error
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    created_by = relationship("User")
    template = relationship("ReportTemplate", back_populates="reports")
    schedules = relationship("ReportSchedule", back_populates="report")


class ReportSchedule(Base):
    """Report schedule model for automated report generation.

    Attributes:
        id: Integer primary key
        report_id: Report reference
        frequency: Execution frequency
        day_of_week: Weekly execution day
        day_of_month: Monthly execution day
        time_of_day: Execution time
        recipients: Email recipients (JSON)
        is_active: Schedule active status
        last_run: Last execution time
        next_run: Next execution time
        created_by_id: Creator user reference
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly
    day_of_week = Column(Integer)  # 0-6 for weekly reports
    day_of_month = Column(Integer)  # 1-31 for monthly reports
    time_of_day = Column(String(5))  # HH:MM format
    recipients = Column(JSON)  # List of email addresses
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    report = relationship("Report", back_populates="schedules")
    created_by = relationship("User")
