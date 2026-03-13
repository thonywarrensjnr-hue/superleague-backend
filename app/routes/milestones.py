from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from app.models.pydantic_models import MilestoneResponse

router = APIRouter(prefix="/api/milestones", tags=["Milestones"])

# Hardcoded milestones matching your design
MILESTONES = [
    {
        "id": uuid.uuid4(),
        "title": "Positive track records and milestones Achieved",
        "description": "24k+ collections, 18k+ artists, 10k+ mints",
        "icon_type": "trophy",
        "display_order": 1
    },
    {
        "id": uuid.uuid4(),
        "title": "Amazing and Unique Arts for the week",
        "description": "Weekly featured art collections",
        "icon_type": "art",
        "display_order": 2
    }
]

@router.get("/", response_model=List[MilestoneResponse])
async def get_milestones():
    """
    Get the milestone items that match the design:
    1. "Positive track records and milestones Achieved" with stats
    2. "Amazing and Unique Arts for the week"
    """
    return MILESTONES

@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "milestones"}