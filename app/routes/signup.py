from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.models.pydantic_models import SignupRequest, SignupResponse, ErrorResponse
from app.services.signup_service import SignupService, get_signup_service
from app.utils.validators import InputValidator
from app.config import settings

router = APIRouter(prefix="/api/signup", tags=["Signup"])


@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Register for early alpha access",
    description="Submit name and email to get early access to the platform",
    responses={
        201: {"description": "Successfully signed up"},
        400: {"description": "Invalid input", "model": ErrorResponse},
        409: {"description": "Email already registered", "model": ErrorResponse},
        429: {"description": "Too many requests", "model": ErrorResponse},
        500: {"description": "Server error", "model": ErrorResponse}
    }
)
async def signup_for_alpha(
        request: Request,
        signup_data: SignupRequest,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    """
    Register a user for early alpha access.

    This endpoint:
    1. Validates the input (name, email)
    2. Checks for duplicate signups
    3. Stores the signup in database
    4. Sends confirmation email
    5. Returns success response

    The design shows a signup form with name and email fields.
    """
    try:
        # Get IP and user agent for tracking
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Create service instance
        service = SignupService(db)

        # Process signup
        result = await service.register_signup(
            signup_data=signup_data,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Prepare response based on result
        if result["status"] == "exists":
            return {
                "status": "already_registered",
                "message": result["message"],
                "email": signup_data.email
            }

        # Return success response
        signup = result["signup"]
        return {
            "status": "success",
            "message": result["message"],
            "id": str(signup.id),
            "name": signup.name,
            "email": signup.email,
            "signed_up_at": signup.signed_up_at.isoformat() if signup.signed_up_at else None
        }

    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup. Please try again later."
        )


@router.get("/check/{email}")
async def check_signup_status(
        email: str,
        db: AsyncSession = Depends(get_db)
):
    """Check if an email is already signed up"""
    try:
        service = SignupService(db)
        signup = await service.get_signup_by_email(email)

        if signup:
            return {
                "registered": True,
                "status": signup.status,
                "signed_up_at": signup.signed_up_at
            }

        return {"registered": False}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking signup status"
        )


@router.get("/stats", summary="Get signup statistics")
async def get_signup_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about signups (admin only in production)"""
    try:
        service = SignupService(db)
        stats = await service.get_signup_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching statistics"
        )


@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "signup"}