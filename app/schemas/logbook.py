from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


class AttachmentBase(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    description: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    pass


class AttachmentUpdate(BaseModel):
    description: Optional[str] = None


class Attachment(AttachmentBase):
    id: UUID
    entry_id: UUID
    uploaded_by_id: UUID
    uploaded_at: datetime
    file_path: str
    is_deleted: bool = False

    class Config:
        orm_mode = True


class LogbookEntryBase(BaseModel):
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
    end_date: Optional[date] = None


class LogbookEntryUpdate(BaseModel):
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
    status: str
    solution_description: Optional[str] = None
    end_date: Optional[date] = None


class LogbookEntry(LogbookEntryBase):
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
    location_name: str
    category_name: Optional[str] = None
    user_full_name: str
    completed_by_name: Optional[str] = None


class LogbookEntrySearch(BaseModel):
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
