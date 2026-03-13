from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from app.models.pydantic_models import TeamMemberResponse

router = APIRouter(prefix="/api/team", tags=["Team"])

# Hardcoded team members matching your design
TEAM_MEMBERS = [
    {
        "id": uuid.uuid4(),
        "name": "Bilikisu wonder",
        "role": "Chief Marketing Officer",
        "bio": "The Calendars, Where New Dates Are Born. Boundaries of Art and Technology.",
        "image_url": None,
        "display_order": 1,
        "social_links": {}
    },
    {
        "id": uuid.uuid4(),
        "name": "John Director",
        "role": "Creative Director",
        "bio": "Leading creative vision and innovation",
        "image_url": None,
        "display_order": 2,
        "social_links": {}
    },
    {
        "id": uuid.uuid4(),
        "name": "Sarah Lead",
        "role": "Lead Artist",
        "bio": "Creating unique artistic experiences",
        "image_url": None,
        "display_order": 3,
        "social_links": {}
    },
    {
        "id": uuid.uuid4(),
        "name": "Mike Tech",
        "role": "Technical Lead",
        "bio": "Building the technology behind the art",
        "image_url": None,
        "display_order": 4,
        "social_links": {}
    }
]


@router.get("/", response_model=List[TeamMemberResponse])
async def get_team_members():
    """
    Get all team members for the 'Meet the Team' section.
    4 team members as shown in the design.
    """
    return TEAM_MEMBERS


@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(member_id: str):
    """Get a specific team member by ID"""
    try:
        from uuid import UUID
        member_id_uuid = UUID(member_id)

        for member in TEAM_MEMBERS:
            if member["id"] == member_id_uuid:
                return member

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid member ID format"
        )


@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "team"}