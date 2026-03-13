from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.sql_models import Milestone
from app.models.pydantic_models import MilestoneResponse

router = APIRouter(prefix="/api/milestones", tags=["Milestones"])


@router.get(
    "/",
    response_model=List[MilestoneResponse],
    summary="Get milestone achievements",
    description="Returns the milestone achievements shown in the design"
)
async def get_milestones(db: AsyncSession = Depends(get_db)):
    """
    Get the milestone items that match the design:
    1. "Positive track records and milestones Achieved"
    2. "Amazing and Unique Arts for the week"
    """
    try:
        # Try to get from database
        query = select(Milestone).where(Milestone.is_active == True).order_by(Milestone.display_order)
        result = await db.execute(query)
        milestones = result.scalars().all()

        if milestones:
            return milestones

        # Return hardcoded milestones matching the design
        return [
            MilestoneResponse(
                id="00000000-0000-0000-0000-000000000001",
                title="Positive track records and milestones Achieved",
                description="Track record of success and achievements",
                icon_type="trophy",
                display_order=1
            ),
            MilestoneResponse(
                id="00000000-0000-0000-0000-000000000002",
                title="Amazing and Unique Arts for the week",
                description="Curated arts and cultural content",
                icon_type="art",
                display_order=2
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching milestones: {str(e)}"
        )


@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "milestones"}