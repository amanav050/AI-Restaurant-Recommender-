import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add app directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.data.repository import RestaurantRepository
from app.domain.models import BudgetBand, UserPreferences, RecommendationResponse
from app.services.recommendation import RecommendationService
from app.core.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="AI Restaurant Recommender API",
    description="API for restaurant recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for caching
repo = None
service = None
settings = None

def initialize_services():
    """Initialize repository and service"""
    global repo, service, settings
    if repo is None:
        repo = RestaurantRepository.from_parquet()
        service = RecommendationService(repo)
        settings = get_settings()

@app.on_event("startup")
async def startup_event():
    initialize_services()

@app.get("/")
async def root():
    return {"message": "AI Restaurant Recommender API", "status": "running"}

@app.get("/health")
async def health_check():
    try:
        initialize_services()
        return {
            "status": "ok", 
            "app": settings.app_name, 
            "environment": settings.environment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cuisines")
async def get_cuisines():
    try:
        initialize_services()
        cuisines = repo.get_unique_cuisines()
        return cuisines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/localities")
async def get_localities():
    try:
        initialize_services()
        localities = repo.get_unique_localities()
        return localities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations")
async def get_recommendations(payload: dict):
    try:
        initialize_services()
        
        # Extract data from payload
        location = payload.get("location")
        budget = payload.get("budget")
        cuisines = payload.get("cuisine", [])
        min_rating = payload.get("min_rating", 0)
        additional_preferences = payload.get("additional_preferences")
        top_k = payload.get("top_k", 5)
        
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        if budget not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Invalid budget. Must be 'low', 'medium', or 'high'")
        
        # Create user preferences
        preferences = UserPreferences(
            location=location.strip(),
            budget=budget,
            cuisines=cuisines if isinstance(cuisines, list) else [cuisines] if cuisines else [],
            min_rating=min_rating,
            additional_preferences=additional_preferences
        )
        
        # Get recommendations
        response = service.recommend(preferences, top_k=top_k)
        
        return response.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preferences")
async def create_preferences(payload: dict):
    try:
        initialize_services()
        
        # Extract and validate data
        location = payload.get("location")
        budget = payload.get("budget")
        cuisines = payload.get("cuisine", [])
        min_rating = payload.get("min_rating", 0)
        additional_preferences = payload.get("additional_preferences")
        
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        if budget not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Invalid budget. Must be 'low', 'medium', or 'high'")
        
        # Create user preferences
        preferences = UserPreferences(
            location=location.strip(),
            budget=budget,
            cuisines=cuisines if isinstance(cuisines, list) else [cuisines] if cuisines else [],
            min_rating=min_rating,
            additional_preferences=additional_preferences
        )
        
        return {"preferences": preferences.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel serverless function handler
handler = app
