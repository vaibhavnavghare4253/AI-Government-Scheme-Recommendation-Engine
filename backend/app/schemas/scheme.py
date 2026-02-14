from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

class SchemeBase(BaseModel):
    scheme_code: str
    name: str
    description: str
    department: str
    category: str
    benefit_type: str
    benefit_amount: Optional[Decimal] = None
    state: Optional[str] = None
    is_central: bool = False
    application_url: Optional[str] = None

class SchemeResponse(SchemeBase):
    id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool

    class Config:
        from_attributes = True

class SchemeListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    schemes: List[SchemeResponse]
