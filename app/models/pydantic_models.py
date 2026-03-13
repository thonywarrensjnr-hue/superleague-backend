from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import re


# ========== Request Models ==========

class SignupRequest(BaseModel):
    """Model for signup request"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: str = Field(..., description="User's email address")
    referral_source: Optional[str] = Field(None, max_length=100, description="How they heard about us")

    @field_validator('name')
    def validate_name(cls, v):
        """Validate name contains only letters, spaces, and hyphens"""
        if not re.match(r'^[a-zA-Z\s\-\.\']+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, periods and apostrophes')
        return v.strip()

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "John Doe",
            "email": "john@example.com",
            "referral_source": "Twitter"
        }
    })


class TeamMemberCreate(BaseModel):
    """Model for creating a team member (admin only)"""
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    image_url: Optional[str] = Field(None, max_length=500)
    display_order: int = Field(0, ge=0)
    social_links: Optional[Dict[str, str]] = Field(default={})

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Bilikisu wonder",
            "role": "Chief Marketing Officer",
            "bio": "The Calendars, Where New Dates Are Born. Boundaries of Art and Technology.",
            "display_order": 1
        }
    })


class MilestoneCreate(BaseModel):
    """Model for creating a milestone"""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    icon_type: str = Field("default", max_length=50)
    display_order: int = Field(0, ge=0)


# ========== Response Models ==========

class SignupResponse(BaseModel):
    """Model for signup response"""
    id: uuid.UUID
    name: str
    email: str
    status: str
    message: str = Field(default="Thanks for signing up! We'll notify you when alpha launches.")
    signed_up_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMemberResponse(BaseModel):
    """Model for team member response"""
    id: uuid.UUID
    name: str
    role: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int
    social_links: Optional[Dict[str, str]] = {}

    model_config = ConfigDict(from_attributes=True)


class MilestoneResponse(BaseModel):
    """Model for milestone response"""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    icon_type: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class InterviewResponse(BaseModel):
    """Model for interview response"""
    id: uuid.UUID
    title: str
    guest_name: str
    guest_title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class HeroContentResponse(BaseModel):
    """Model for hero content response"""
    headline: str
    subheadline: Optional[str] = None
    description: Optional[str] = None
    primary_cta_text: str
    primary_cta_link: str

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "detail": "Email already registered",
            "error_code": "DUPLICATE_EMAIL"
        }
    })


# ========== Pagination ==========

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int