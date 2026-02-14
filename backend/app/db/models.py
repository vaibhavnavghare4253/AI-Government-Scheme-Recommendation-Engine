from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, TIMESTAMP, Text, ForeignKey, ARRAY, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cognito_id = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    recommendations = relationship("Recommendation", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    full_name = Column(String(255))
    age = Column(Integer)
    gender = Column(String(20))
    annual_income = Column(DECIMAL(12, 2))
    caste_category = Column(String(50))
    state = Column(String(100))
    district = Column(String(100))
    block = Column(String(100))
    village = Column(String(100))
    occupation = Column(String(100))
    family_size = Column(Integer)
    is_bpl = Column(Boolean)
    has_disability = Column(Boolean)
    education_level = Column(String(50))
    land_ownership = Column(DECIMAL(10, 2))
    preferred_language = Column(String(10), default='en')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="profile")

class Scheme(Base):
    __tablename__ = "schemes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(500), nullable=False)
    name_hi = Column(Text)
    name_mr = Column(Text)
    name_ta = Column(Text)
    description = Column(Text)
    description_hi = Column(Text)
    description_mr = Column(Text)
    description_ta = Column(Text)
    department = Column(String(255))
    category = Column(String(100))
    benefit_type = Column(String(100))
    benefit_amount = Column(DECIMAL(12, 2))
    state = Column(String(100))
    is_central = Column(Boolean, default=False)
    application_url = Column(Text)
    document_url = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    eligibility_rules = relationship("EligibilityRule", back_populates="scheme")
    recommendations = relationship("Recommendation", back_populates="scheme")
    documents = relationship("SchemeDocument", back_populates="scheme")

class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"))
    rule_type = Column(String(50))
    operator = Column(String(20))
    value_min = Column(DECIMAL(12, 2))
    value_max = Column(DECIMAL(12, 2))
    value_list = Column(ARRAY(Text))
    is_mandatory = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    scheme = relationship("Scheme", back_populates="eligibility_rules")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"))
    match_score = Column(DECIMAL(5, 2))
    explanation = Column(Text)
    explanation_hi = Column(Text)
    explanation_mr = Column(Text)
    explanation_ta = Column(Text)
    document_checklist = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    viewed_at = Column(TIMESTAMP)
    applied_at = Column(TIMESTAMP)
    
    user = relationship("User", back_populates="recommendations")
    scheme = relationship("Scheme", back_populates="recommendations")

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"))
    interaction_type = Column(String(50))
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    user = relationship("User", back_populates="interactions")

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cognito_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default='admin')
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class SchemeDocument(Base):
    __tablename__ = "scheme_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"))
    s3_key = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_type = Column(String(50))
    file_size = Column(Integer)
    processing_status = Column(String(50), default='pending')
    extracted_text = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    processed_at = Column(TIMESTAMP)
    
    scheme = relationship("Scheme", back_populates="documents")
