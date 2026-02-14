from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.db import models
from app.schemas.scheme import SchemeResponse, SchemeListResponse

router = APIRouter()

@router.get("/", response_model=SchemeListResponse)
async def list_schemes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    state: Optional[str] = None,
    category: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """List all schemes with optional filters"""
    query = db.query(models.Scheme).filter(models.Scheme.is_active == is_active)
    
    if state:
        query = query.filter(models.Scheme.state == state)
    if category:
        query = query.filter(models.Scheme.category == category)
    
    total = query.count()
    schemes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "schemes": schemes
    }

@router.get("/{scheme_id}", response_model=SchemeResponse)
async def get_scheme(
    scheme_id: UUID,
    db: Session = Depends(get_db)
):
    """Get scheme details by ID"""
    scheme = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.get("/search/", response_model=SchemeListResponse)
async def search_schemes(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search schemes by name or description"""
    query = db.query(models.Scheme).filter(
        models.Scheme.is_active == True,
        (models.Scheme.name.ilike(f"%{q}%") | models.Scheme.description.ilike(f"%{q}%"))
    )
    
    total = query.count()
    schemes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "schemes": schemes
    }

@router.get("/categories/")
async def get_categories(db: Session = Depends(get_db)):
    """Get all scheme categories"""
    categories = db.query(models.Scheme.category).distinct().all()
    return {"categories": [cat[0] for cat in categories if cat[0]]}
