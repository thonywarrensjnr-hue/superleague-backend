from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import uuid

from app.models.sql_models import AlphaSignup
from app.models.pydantic_models import SignupRequest, SignupResponse
from app.services.email_service import email_service
from app.utils.validators import InputValidator

logger = logging.getLogger(__name__)


class SignupService:
    """Service for handling signups"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = InputValidator()

    async def register_signup(
            self,
            signup_data: SignupRequest,
            ip_address: Optional[str] = None,
            user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new signup"""
        try:
            # Check for existing signup
            existing = await self.get_signup_by_email(signup_data.email)
            if existing:
                return {
                    "status": "exists",
                    "message": "You're already on our list! We'll be in touch soon.",
                    "signup": existing
                }

            # Create new signup
            new_signup = AlphaSignup(
                id=uuid.uuid4(),
                name=signup_data.name.strip(),
                email=signup_data.email.lower().strip(),
                referral_source=signup_data.referral_source,
                ip_address=ip_address,
                user_agent=user_agent,
                status='pending'
            )

            self.db.add(new_signup)
            await self.db.commit()
            await self.db.refresh(new_signup)

            # Send welcome email (don't await - let it run in background)
            try:
                await email_service.send_welcome_email(
                    new_signup.email,
                    new_signup.name
                )
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")

            # Notify admin (don't await)
            try:
                await email_service.send_admin_notification({
                    'name': new_signup.name,
                    'email': new_signup.email,
                    'signed_up_at': new_signup.signed_up_at
                })
            except Exception as e:
                logger.error(f"Failed to send admin notification: {e}")

            return {
                "status": "success",
                "message": "Thanks for signing up! Check your email for confirmation.",
                "signup": new_signup
            }

        except Exception as e:
            logger.error(f"Error registering signup: {e}")
            await self.db.rollback()
            raise

    async def get_signup_by_email(self, email: str) -> Optional[AlphaSignup]:
        """Get signup by email"""
        query = select(AlphaSignup).where(AlphaSignup.email == email.lower().strip())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_signups(
            self,
            skip: int = 0,
            limit: int = 50,
            status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all signups with pagination"""
        query = select(AlphaSignup).order_by(AlphaSignup.signed_up_at.desc())

        if status:
            query = query.where(AlphaSignup.status == status)

        # Get total count
        count_query = select(AlphaSignup)
        if status:
            count_query = count_query.where(AlphaSignup.status == status)
        total = len((await self.db.execute(count_query)).scalars().all())

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        signups = result.scalars().all()

        return {
            "items": signups,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }

    async def update_signup_status(self, signup_id: uuid.UUID, status: str) -> Optional[AlphaSignup]:
        """Update signup status"""
        signup = await self.db.get(AlphaSignup, signup_id)
        if signup:
            signup.status = status
            if status == 'invited':
                signup.invited_at = datetime.utcnow()
                signup.invite_sent_count += 1
            elif status == 'converted':
                signup.converted_to_user = True

            await self.db.commit()
            await self.db.refresh(signup)

        return signup

    async def get_signup_stats(self) -> Dict[str, Any]:
        """Get signup statistics"""
        # Total signups
        total_query = select(AlphaSignup)
        total = len((await self.db.execute(total_query)).scalars().all())

        # Today's signups
        today = datetime.utcnow().date()
        today_query = select(AlphaSignup).where(
            AlphaSignup.signed_up_at >= today
        )
        today_count = len((await self.db.execute(today_query)).scalars().all())

        # By status
        statuses = {}
        for status in ['pending', 'approved', 'invited', 'converted']:
            status_query = select(AlphaSignup).where(AlphaSignup.status == status)
            statuses[status] = len((await self.db.execute(status_query)).scalars().all())

        return {
            "total": total,
            "today": today_count,
            "by_status": statuses,
            "conversion_rate": (statuses.get('converted', 0) / total * 100) if total > 0 else 0
        }


def get_signup_service(db: AsyncSession) -> SignupService:
    """Dependency to get signup service"""
    return SignupService(db)