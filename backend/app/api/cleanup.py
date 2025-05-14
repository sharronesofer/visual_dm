from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import CleanupRule, CleanupEntry
from .schemas import (
    CleanupRuleCreate,
    CleanupRuleResponse,
    CleanupRuleUpdate,
    CleanupEntryCreate,
    CleanupEntryResponse,
    CleanupEntryUpdate
)

router = APIRouter()

# Cleanup Rules endpoints
@router.get("/rules", response_model=List[CleanupRuleResponse])
async def list_cleanup_rules(db: Session = Depends(get_db)):
    """List all cleanup rules."""
    rules = db.query(CleanupRule).all()
    return rules

@router.post("/rules", response_model=CleanupRuleResponse)
async def create_cleanup_rule(rule: CleanupRuleCreate, db: Session = Depends(get_db)):
    """Create a new cleanup rule."""
    db_rule = CleanupRule(**rule.dict())
    db.add(db_rule)
    try:
        db.commit()
        db.refresh(db_rule)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_rule

@router.get("/rules/{rule_id}", response_model=CleanupRuleResponse)
async def get_cleanup_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific cleanup rule by ID."""
    rule = db.query(CleanupRule).filter(CleanupRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Cleanup rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=CleanupRuleResponse)
async def update_cleanup_rule(
    rule_id: int,
    rule_update: CleanupRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a cleanup rule."""
    db_rule = db.query(CleanupRule).filter(CleanupRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Cleanup rule not found")
    
    for field, value in rule_update.dict(exclude_unset=True).items():
        setattr(db_rule, field, value)
    
    try:
        db.commit()
        db.refresh(db_rule)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_rule

@router.delete("/rules/{rule_id}")
async def delete_cleanup_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a cleanup rule."""
    db_rule = db.query(CleanupRule).filter(CleanupRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Cleanup rule not found")
    
    try:
        db.delete(db_rule)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Cleanup rule deleted successfully"}

# Cleanup Entries endpoints
@router.get("/entries", response_model=List[CleanupEntryResponse])
async def list_cleanup_entries(db: Session = Depends(get_db)):
    """List all cleanup entries."""
    entries = db.query(CleanupEntry).all()
    return entries

@router.post("/entries", response_model=CleanupEntryResponse)
async def create_cleanup_entry(entry: CleanupEntryCreate, db: Session = Depends(get_db)):
    """Create a new cleanup entry."""
    db_entry = CleanupEntry(**entry.dict())
    db.add(db_entry)
    try:
        db.commit()
        db.refresh(db_entry)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_entry

@router.get("/entries/{entry_id}", response_model=CleanupEntryResponse)
async def get_cleanup_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific cleanup entry by ID."""
    entry = db.query(CleanupEntry).filter(CleanupEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Cleanup entry not found")
    return entry

@router.put("/entries/{entry_id}", response_model=CleanupEntryResponse)
async def update_cleanup_entry(
    entry_id: int,
    entry_update: CleanupEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a cleanup entry."""
    db_entry = db.query(CleanupEntry).filter(CleanupEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Cleanup entry not found")
    
    for field, value in entry_update.dict(exclude_unset=True).items():
        setattr(db_entry, field, value)
    
    try:
        db.commit()
        db.refresh(db_entry)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_entry

@router.delete("/entries/{entry_id}")
async def delete_cleanup_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a cleanup entry."""
    db_entry = db.query(CleanupEntry).filter(CleanupEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Cleanup entry not found")
    
    try:
        db.delete(db_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Cleanup entry deleted successfully"} 