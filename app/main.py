from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time

from app.routes import hero, team, milestones, signup

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Superleague API",
    description="Backend API for Superleague projects",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    return response

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
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
            "docs": "/api/docs"
        }
    }

# Health check
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Global health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": ["hero", "team", "milestones", "signup"]
    }