from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.database import db_manager
from app.routes import hero, team, milestones, signup

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events
    """
    # Startup
    logger.info("Starting up Superleague API...")
    try:
        # Create tables if they don't exist (for development)
        if settings.ENVIRONMENT == "development":
            await db_manager.create_tables()
            logger.info("Database tables ready")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Superleague API...")
    # Close database connections
    await db_manager.engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Superleague API",
    description="Backend API for Superleague celebrity interview platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and their processing time"""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "path": request.url.path
        },
    )


# Include routers
app.include_router(hero.router)
app.include_router(team.router)
app.include_router(milestones.router)
app.include_router(signup.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": "Superleague API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "hero": "/api/hero/content",
            "team": "/api/team/",
            "milestones": "/api/milestones/",
            "signup": "/api/signup/",
            "docs": "/api/docs" if settings.DEBUG else "Disabled in production"
        }
    }


# Health check
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Global health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "hero": "up",
            "team": "up",
            "milestones": "up",
            "signup": "up"
        }
    }


# For local development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )