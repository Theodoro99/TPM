from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
import uuid
from datetime import date

from app.core.security import get_current_active_user, is_manager_or_admin, create_audit_log
from app.db.database import get_db
from app.db.models import LogbookEntry, User, Attachment, Location, Category
from app.schemas.logbook import (
    LogbookEntryCreate, 
    LogbookEntryUpdate, 
    LogbookEntry as LogbookEntrySchema,
    LogbookEntryDetail,
    LogbookEntryStatusUpdate,
    LogbookEntrySearch
)
from app.services.file_service import save_upload_file

router = APIRouter(
    prefix="/logbook",
    tags=["logbook"],
    responses={404: {"description": "Not found"}},
)


@router.post("/entries", response_model=LogbookEntrySchema, status_code=status.HTTP_201_CREATED)
async def create_logbook_entry(
    entry: LogbookEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new logbook entry.
    """
    # Verify location exists
    location = db.query(Location).filter(Location.id == entry.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Verify category exists if provided
    if entry.category_id:
        category = db.query(Category).filter(Category.id == entry.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Create new entry
    db_entry = LogbookEntry(
        user_id=current_user.id,
        **entry.dict()
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create",
        entity_type="logbook_entry",
        entity_id=str(db_entry.id)
    )
    
    return db_entry


@router.get("/entries", response_model=List[LogbookEntrySchema])
async def read_logbook_entries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve logbook entries with optional filtering.
    Managers and admins can see all entries, technicians can only see their own.
    """
    query = db.query(LogbookEntry).filter(LogbookEntry.is_deleted == False)
    
    # Apply role-based filtering
    if current_user.role == "technician":
        query = query.filter(LogbookEntry.user_id == current_user.id)
    
    # Apply filters if provided
    if status:
        query = query.filter(LogbookEntry.status == status)
    if start_date_from:
        query = query.filter(LogbookEntry.start_date >= start_date_from)
    if start_date_to:
        query = query.filter(LogbookEntry.start_date <= start_date_to)
    if location_id:
        query = query.filter(LogbookEntry.location_id == location_id)
    
    # Order by most recent first
    query = query.order_by(LogbookEntry.created_at.desc())
    
    # Apply pagination
    entries = query.offset(skip).limit(limit).all()
    return entries


@router.get("/entries/{entry_id}", response_model=LogbookEntryDetail)
async def read_logbook_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific logbook entry by ID.
    """
    entry = db.query(LogbookEntry).filter(LogbookEntry.id == entry_id, LogbookEntry.is_deleted == False).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Check if user has permission to view this entry
    if current_user.role == "technician" and entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this entry")
    
    # Get additional data for detailed view
    location_name = entry.location.name if entry.location else "Unknown"
    category_name = entry.category.name if entry.category else None
    user_full_name = entry.user.full_name if entry.user else "Unknown"
    completed_by_name = entry.completed_by.full_name if entry.completed_by else None
    
    # Create detailed response
    result = LogbookEntryDetail(
        **{k: v for k, v in entry.__dict__.items() if not k.startswith('_')},
        location_name=location_name,
        category_name=category_name,
        user_full_name=user_full_name,
        completed_by_name=completed_by_name
    )
    
    return result


@router.put("/entries/{entry_id}", response_model=LogbookEntrySchema)
async def update_logbook_entry(
    entry_id: uuid.UUID,
    entry_update: LogbookEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing logbook entry.
    """
    db_entry = db.query(LogbookEntry).filter(LogbookEntry.id == entry_id, LogbookEntry.is_deleted == False).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Check if user has permission to update this entry
    if current_user.role == "technician" and db_entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this entry")
    
    # Verify location exists if being updated
    if entry_update.location_id is not None:
        location = db.query(Location).filter(Location.id == entry_update.location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
    
    # Verify category exists if being updated
    if entry_update.category_id is not None:
        category = db.query(Category).filter(Category.id == entry_update.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Update entry fields
    update_data = entry_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)
    
    # If status is being changed to completed, set completed_by
    if update_data.get("status") == "completed" and db_entry.status != "completed":
        db_entry.completed_by_id = current_user.id
    
    db.commit()
    db.refresh(db_entry)
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update",
        entity_type="logbook_entry",
        entity_id=str(entry_id),
        details=update_data
    )
    
    return db_entry


@router.patch("/entries/{entry_id}/status", response_model=LogbookEntrySchema)
async def update_entry_status(
    entry_id: uuid.UUID,
    status_update: LogbookEntryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of a logbook entry.
    """
    db_entry = db.query(LogbookEntry).filter(LogbookEntry.id == entry_id, LogbookEntry.is_deleted == False).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Check if user has permission to update this entry
    if current_user.role == "technician" and db_entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this entry")
    
    # Update status
    db_entry.status = status_update.status
    
    # Update solution description if provided
    if status_update.solution_description:
        db_entry.solution_description = status_update.solution_description
    
    # Update end date if provided
    if status_update.end_date:
        db_entry.end_date = status_update.end_date
    
    # If status is being changed to completed, set completed_by
    if status_update.status == "completed" and db_entry.status != "completed":
        db_entry.completed_by_id = current_user.id
    
    db.commit()
    db.refresh(db_entry)
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="status_update",
        entity_type="logbook_entry",
        entity_id=str(entry_id),
        details=status_update.dict()
    )
    
    return db_entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logbook_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete a logbook entry.
    """
    db_entry = db.query(LogbookEntry).filter(LogbookEntry.id == entry_id, LogbookEntry.is_deleted == False).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Only managers and admins can delete entries, or the owner if it's a technician
    if current_user.role == "technician" and db_entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
    
    # Soft delete
    db_entry.is_deleted = True
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete",
        entity_type="logbook_entry",
        entity_id=str(entry_id)
    )
    
    return None


@router.post("/entries/{entry_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    entry_id: uuid.UUID,
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file attachment for a logbook entry.
    """
    # Check if entry exists
    entry = db.query(LogbookEntry).filter(LogbookEntry.id == entry_id, LogbookEntry.is_deleted == False).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Check if user has permission to add attachment to this entry
    if current_user.role == "technician" and entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add attachments to this entry")
    
    # Save the file
    file_path, file_size = await save_upload_file(file, entry_id)
    
    # Create attachment record
    attachment = Attachment(
        entry_id=entry_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file_size,
        description=description,
        uploaded_by_id=current_user.id
    )
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="upload_attachment",
        entity_type="attachment",
        entity_id=str(attachment.id),
        details={"file_name": file.filename, "entry_id": str(entry_id)}
    )
    
    return {"id": attachment.id, "file_name": attachment.file_name}


@router.post("/search", response_model=List[LogbookEntrySchema])
async def search_logbook_entries(
    search_params: LogbookEntrySearch,
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Advanced search for logbook entries.
    """
    query = db.query(LogbookEntry).filter(LogbookEntry.is_deleted == False)
    
    # Apply role-based filtering
    if current_user.role == "technician":
        query = query.filter(LogbookEntry.user_id == current_user.id)
    
    # Apply search filters
    if search_params.start_date_from:
        query = query.filter(LogbookEntry.start_date >= search_params.start_date_from)
    if search_params.start_date_to:
        query = query.filter(LogbookEntry.start_date <= search_params.start_date_to)
    if search_params.status:
        query = query.filter(LogbookEntry.status == search_params.status)
    if search_params.location_id:
        query = query.filter(LogbookEntry.location_id == search_params.location_id)
    if search_params.device:
        query = query.filter(LogbookEntry.device.ilike(f"%{search_params.device}%"))
    if search_params.responsible_person:
        query = query.filter(LogbookEntry.responsible_person.ilike(f"%{search_params.responsible_person}%"))
    if search_params.category_id:
        query = query.filter(LogbookEntry.category_id == search_params.category_id)
    if search_params.priority:
        query = query.filter(LogbookEntry.priority == search_params.priority)
    if search_params.user_id and (current_user.role in ["admin", "manager"]):
        query = query.filter(LogbookEntry.user_id == search_params.user_id)
    
    # Text search in description fields
    if search_params.search_text:
        search_term = f"%{search_params.search_text}%"
        query = query.filter(
            (LogbookEntry.call_description.ilike(search_term)) |
            (LogbookEntry.solution_description.ilike(search_term)) |
            (LogbookEntry.device.ilike(search_term))
        )
    
    # Order by most recent first
    query = query.order_by(LogbookEntry.created_at.desc())
    
    # Apply pagination
    entries = query.offset(skip).limit(limit).all()
    return entries
