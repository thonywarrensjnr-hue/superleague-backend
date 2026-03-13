from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sql_models import HeroContent
from app.models.pydantic_models import HeroContentResponse

router = APIRouter(prefix="/api/hero", tags=["Hero Section"])


@router.get(
    "/content",
    response_model=HeroContentResponse,
    summary="Get hero section content",
    description="Returns the main hero section content including headline and description"
)
async def get_hero_content(db: AsyncSession = Depends(get_db)):
    """
    Get the hero section content that matches the design:
    - Headline: "vaishali maruti chandane"
    - Subheadline: "Ready to Own History"
    - Description: "Join the first of Vaishali's Celebrity Interviews..."
    """
    try:
        # Try to get from database first
        from sqlalchemy import select
        query = select(HeroContent).where(HeroContent.is_active == True)
        result = await db.execute(query)
        content = result.scalar_one_or_none()

        if content:
            return content

        # Return hardcoded content matching the design
        return HeroContentResponse(
            headline="vaishali maruti chandane",
            subheadline="Ready to Own History",
            description="Join the first of Vaishali's Celebrity Interviews with a new perspective on history.",
            primary_cta_text="Sign up for early Alpha",
            primary_cta_link="/signup"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hero content: {str(e)}"
        )


@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "hero"}