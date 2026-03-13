from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Index, JSON
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
import uuid

from app.database import Base


class AlphaSignup(Base):
    """Model for early access signups"""
    __tablename__ = "alpha_signups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    signed_up_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default='pending')  # pending, approved, invited, converted
    referral_source = Column(String(100), nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)

    # Tracking
    converted_to_user = Column(Boolean, default=False)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    invite_sent_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_signups_email', email),
        Index('idx_signups_status', status),
        Index('idx_signups_created', created_at),
    )

    def __repr__(self):
        return f"<AlphaSignup {self.email}>"


class TeamMember(Base):
    """Model for team members"""
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)

    # Social links (optional)
    social_links = Column(JSON, default={})  # Store as JSON: {"linkedin": "url", "twitter": "url"}

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<TeamMember {self.name}>"


class Milestone(Base):
    """Model for milestone achievements"""
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_type = Column(String(50), default='default')  # trophy, art, star, etc.
    display_order = Column(Integer, default=0)

    # Additional data
    value = Column(String(100), nullable=True)  # e.g., "100+", "10 years"
    category = Column(String(50), default='general')

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Milestone {self.title}>"


class Interview(Base):
    """Model for upcoming interviews"""
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    guest_name = Column(String(255), nullable=False)
    guest_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(50), default='upcoming')  # upcoming, live, completed, cancelled

    # Media
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)

    # Metadata
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Interview {self.title}>"


class HeroContent(Base):
    """Model for hero section content"""
    __tablename__ = "hero_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    headline = Column(String(255), nullable=False)
    subheadline = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # CTA buttons
    primary_cta_text = Column(String(50), default="Sign Up")
    primary_cta_link = Column(String(500), default="/signup")
    secondary_cta_text = Column(String(50), nullable=True)
    secondary_cta_link = Column(String(500), nullable=True)

    # Background image/video
    background_image = Column(String(500), nullable=True)
    background_video = Column(String(500), nullable=True)

    # Version control
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<HeroContent {self.headline}>"