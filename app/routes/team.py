from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.sql_models import TeamMember
from app.models.pydantic_models import TeamMemberResponse

router = APIRouter(prefix="/api/team", tags=["Team"])


@router.get(
    "/",
    response_model=List[TeamMemberResponse],
    summary="Get team members",
    description="Returns the team members for the 'Meet the Team' section"
)
async def get_team_members(db: AsyncSession = Depends(get_db)):
    """
    Get all active team members ordered by display order.
    Matches the design's "Meet the Team" section.
    """
    try:
        # Try to get from database
        query = select(TeamMember).where(
            TeamMember.is_active == True
        ).order_by(TeamMember.display_order)

        result = await db.execute(query)
        members = result.scalars().all()

        if members:
            return members

        # Return hardcoded team member from your screenshot
        return [
            TeamMemberResponse(
                id="00000000-0000-0000-0000-000000000001",
                name="Bilikisu wonder",
                role="Chief Marketing Officer",
                bio="The Calendars, Where New Dates Are Born. Boundaries of Art and Technology.",
                image_url=None,
                display_order=1,
                social_links={}
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching team members: {str(e)}"
        )


@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(member_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific team member by ID"""
    try:
        from sqlalchemy import select
        from uuid import UUID

        query = select(TeamMember).where(TeamMember.id == UUID(member_id))
        result = await db.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )

        return member
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid member ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching team member: {str(e)}"
        )


@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "team"}