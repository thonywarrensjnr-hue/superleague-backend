from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.models.pydantic_models import SignupRequest, SignupResponse

router = APIRouter(prefix="/api/signup", tags=["Signup"])

# In-memory storage for Vercel (resets on each deploy)
# For production, you'd use a real database
signups_db = []


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def signup(request: Request, signup_data: SignupRequest):
    """
    Register a user for early alpha access.
    Using in-memory storage for Vercel deployment.
    """
    try:
        # Check if email already exists (in our memory storage)
        for existing in signups_db:
            if existing["email"] == signup_data.email:
                return {
                    "status": "already_registered",
                    "message": "You're already on our list! We'll be in touch soon.",
                    "email": signup_data.email
                }

        # Create new signup
        new_signup = {
            "id": str(uuid.uuid4()),
            "name": signup_data.name,
            "email": signup_data.email,
            "referral_source": signup_data.referral_source,
            "signed_up_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # Store in memory
        signups_db.append(new_signup)

        # Return success
        return {
            "status": "success",
            "message": f"Thanks {signup_data.name}! Check your email for confirmation.",
            "id": new_signup["id"],
            "name": new_signup["name"],
            "email": new_signup["email"],
            "signed_up_at": new_signup["signed_up_at"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )


@router.get("/list")
async def get_all_signups():
    """Get all signups (for testing purposes)"""
    return {
        "total": len(signups_db),
        "signups": signups_db
    }


@router.get("/health", summary="Health check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "signup", "total_signups": len(signups_db)}