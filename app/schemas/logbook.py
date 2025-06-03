from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field

"""Pydantic schemas for request/response data validation.

This module contains all data models used for API request validation and response formatting.
The schemas provide type hints, validation, and serialization for the application's data structures.
"""

class AttachmentBase(BaseModel):
    """Base schema for attachment data.

    Fields:
        file_name: Name of the attached file
        file_type: MIME type of the file
        file_size: Size of file in bytes
        description: Optional description of the attachment
    """
    file_name: str
    file_type: str
    file_size: int
    description: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    """Schema for creating new attachments (extends AttachmentBase)."""
    pass


class AttachmentUpdate(BaseModel):
    """Schema for updating attachment metadata.

    Fields:
        description: New description for the attachment
    """
    description: Optional[str] = None


class Attachment(AttachmentBase):
    """Complete attachment schema including database fields.

    Fields:
        id: Unique attachment identifier
        entry_id: Associated logbook entry ID
        uploaded_by_id: User who uploaded the file
        uploaded_at: Timestamp of upload
        file_path: Server storage path
        is_deleted: Soft deletion flag
    """
    id: UUID
    entry_id: UUID
    uploaded_by_id: UUID
    uploaded_at: datetime
    file_path: str
    is_deleted: bool = False

    class Config:
        orm_mode = True


class LogbookEntryBase(BaseModel):
    """Base schema for logbook entry data.

    Fields:
        start_date: When the entry was created
        responsible_person: Person responsible
        location_id: Associated location ID
        device: Device/equipment involved
        call_description: Description of the issue
        solution_description: Resolution details (optional)
        status: Current status (default: 'open')
        downtime_hours: Hours of downtime (optional)
        priority: Priority level (default: 'medium')
        category_id: Category ID (optional)
    """
    start_date: date
    responsible_person: str
    location_id: int
    device: str
    call_description: str
    solution_description: Optional[str] = None
    status: str = "open"
    downtime_hours: Optional[float] = None
    priority: str = "medium"
    category_id: Optional[int] = None


class LogbookEntryCreate(LogbookEntryBase):
    """Schema for creating new logbook entries (extends LogbookEntryBase).

    Fields:
        end_date: Completion date (optional)
    """
    end_date: Optional[date] = None


class LogbookEntryUpdate(BaseModel):
    """Schema for updating logbook entries.

    Fields:
        end_date: New completion date (optional)
        responsible_person: Updated responsible person (optional)
        location_id: New location ID (optional)
        device: Updated device name (optional)
        call_description: Updated issue description (optional)
        solution_description: Updated resolution details (optional)
        status: New status (optional)
        downtime_hours: Updated downtime hours (optional)
        priority: New priority level (optional)
        category_id: New category ID (optional)
    """
    end_date: Optional[date] = None
    responsible_person: Optional[str] = None
    location_id: Optional[int] = None
    device: Optional[str] = None
    call_description: Optional[str] = None
    solution_description: Optional[str] = None
    status: Optional[str] = None
    downtime_hours: Optional[float] = None
    priority: Optional[str] = None
    category_id: Optional[int] = None


class LogbookEntryStatusUpdate(BaseModel):
    """Schema for updating entry status.

    Fields:
        status: New status value
        solution_description: Resolution details (optional)
        end_date: Completion date (optional)
    """
    status: str
    solution_description: Optional[str] = None
    end_date: Optional[date] = None


class LogbookEntry(LogbookEntryBase):
    """Complete logbook entry schema including database fields.

    Fields:
        id: Unique entry identifier
        user_id: Creator user ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
        end_date: Completion date (optional)
        completed_by_id: User who completed the entry (optional)
        is_deleted: Soft deletion flag
        attachments: List of associated attachments
    """
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    end_date: Optional[date] = None
    completed_by_id: Optional[UUID] = None
    is_deleted: bool = False
    attachments: List[Attachment] = []

    class Config:
        orm_mode = True


class LogbookEntryDetail(LogbookEntry):
    """Extended logbook entry schema with related data.

    Fields:
        location_name: Name of associated location
        category_name: Name of associated category (optional)
        user_full_name: Full name of creator
        completed_by_name: Full name of completer (optional)
    """

    location_name: str
    category_name: Optional[str] = None
    user_full_name: str
    completed_by_name: Optional[str] = None


class LogbookEntrySearch(BaseModel):
    """Schema for logbook entry search parameters.

    Fields:
        start_date_from: Filter entries after this date (optional)
        start_date_to: Filter entries before this date (optional)
        status: Filter by status (optional)
        location_id: Filter by location ID (optional)
        device: Filter by device name (optional)
        responsible_person: Filter by responsible person (optional)
        category_id: Filter by category ID (optional)
        priority: Filter by priority level (optional)
        search_text: Full-text search term (optional)
        user_id: Filter by creator user ID (optional)
    """

    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    status: Optional[str] = None
    location_id: Optional[int] = None
    device: Optional[str] = None
    responsible_person: Optional[str] = None
    category_id: Optional[int] = None
    priority: Optional[str] = None
    search_text: Optional[str] = None
    user_id: Optional[UUID] = None
