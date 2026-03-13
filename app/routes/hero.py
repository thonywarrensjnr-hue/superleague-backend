from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime

from app.models.pydantic_models import HeroContentResponse

router = APIRouter(prefix="/api/hero", tags=["Hero Section"])

# Hardcoded data matching your design
HERO_CONTENT = {
    "headline": "Get Ready to Own a Piece of History",
    "subheadline": "Ready to Own History",
    "description": "Join the first of Vaishali's Celebrity Interviews with a new perspective on history.",
    "primary_cta_text": "Sign up for early Alpha",
    "primary_cta_link": "/signup"
}

@router.get(
    "/content",
    response_model=HeroContentResponse,
    summary="Get hero section content",
    description="Returns the main hero section content including headline and description"
)
async def get_hero_content():
    """
    Get the hero section content that matches the design.
    Using hardcoded data for Vercel deployment.
    """
    return HeroContentResponse(
        headline=HERO_CONTENT["headline"],
        subheadline=HERO_CONTENT["subheadline"],
        description=HERO_CONTENT["description"],
        primary_cta_text=HERO_CONTENT["primary_cta_text"],
        primary_cta_link=HERO_CONTENT["primary_cta_link"]
    )

@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "hero"}