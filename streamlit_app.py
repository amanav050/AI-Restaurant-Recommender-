import os
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import sys

# Add the app directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.data.repository import RestaurantRepository
from app.domain.models import BudgetBand, UserPreferences, RecommendationResponse
from app.services.recommendation import RecommendationService
from app.core.config import get_settings

# Configure Streamlit page
st.set_page_config(
    page_title="AI Restaurant Recommender",
    page_icon=":restaurant:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'repo' not in st.session_state:
    st.session_state.repo = None
if 'service' not in st.session_state:
    st.session_state.service = None
if 'settings' not in st.session_state:
    st.session_state.settings = None

def initialize_services():
    """Initialize repository and service with caching"""
    try:
        if st.session_state.repo is None:
            st.session_state.repo = RestaurantRepository.from_parquet()
            st.session_state.service = RecommendationService(st.session_state.repo)
            st.session_state.settings = get_settings()
        return True
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        return False

def health_check() -> Dict[str, Any]:
    """Health check endpoint equivalent"""
    if not initialize_services():
        return {"status": "error", "app": "AI Restaurant Recommender", "environment": "unknown"}
    
    return {
        "status": "ok", 
        "app": st.session_state.settings.app_name, 
        "environment": st.session_state.settings.environment
    }

def get_cuisines() -> List[str]:
    """Get available cuisines"""
    if not initialize_services():
        return []
    return st.session_state.repo.get_unique_cuisines()

def get_localities() -> List[str]:
    """Get available localities"""
    if not initialize_services():
        return []
    return st.session_state.repo.get_unique_localities()

def create_preferences(location: str, budget: str, cuisines: List[str], 
                      min_rating: float, additional_preferences: str = None) -> UserPreferences:
    """Create user preferences object"""
    return UserPreferences(
        location=location.strip(),
        budget=budget,
        cuisines=cuisines,
        min_rating=min_rating,
        additional_preferences=additional_preferences
    )

def get_recommendations(preferences: UserPreferences, top_k: int = 5) -> RecommendationResponse:
    """Get recommendations based on user preferences"""
    if not initialize_services():
        return None
    return st.session_state.service.recommend(preferences, top_k=top_k)

def main():
    st.title("AI Restaurant Recommender")
    st.markdown("Get personalized restaurant recommendations powered by AI")
    
    # Initialize services
    if not initialize_services():
        st.error("Failed to initialize the application. Please check your configuration.")
        return
    
    # Sidebar for user input
    st.sidebar.header("Your Preferences")
    
    # Location input
    available_localities = get_localities()
    location = st.sidebar.selectbox(
        "Select Location",
        options=available_localities,
        index=0 if available_localities else None,
        help="Choose your preferred location"
    )
    
    # Budget selection
    budget = st.sidebar.selectbox(
        "Budget Range",
        options=["low", "medium", "high"],
        index=1,  # Default to medium
        format_func=lambda x: x.capitalize(),
        help="Select your budget preference"
    )
    
    # Cuisine selection
    available_cuisines = get_cuisines()
    selected_cuisines = st.sidebar.multiselect(
        "Preferred Cuisines",
        options=available_cuisines,
        default=[],
        help="Select your preferred cuisines (leave empty for no preference)"
    )
    
    # Rating preference
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=5.0,
        value=3.5,
        step=0.1,
        help="Minimum restaurant rating"
    )
    
    # Additional preferences
    additional_preferences = st.sidebar.text_area(
        "Additional Preferences (Optional)",
        placeholder="e.g., outdoor seating, live music, family-friendly...",
        help="Any specific requirements or preferences"
    )
    
    # Number of recommendations
    top_k = st.sidebar.slider(
        "Number of Recommendations",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        help="How many recommendations would you like?"
    )
    
    # Main content area
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Health Check")
        health_status = health_check()
        if health_status["status"] == "ok":
            st.success(f"Status: {health_status['status'].upper()}")
            st.info(f"Environment: {health_status['environment']}")
        else:
            st.error(f"Status: {health_status['status'].upper()}")
    
    with col2:
        st.subheader("Get Recommendations")
        
        # Get recommendations button
        if st.button("Get Recommendations", type="primary"):
            with st.spinner("Analyzing your preferences and generating recommendations..."):
                try:
                    # Create user preferences
                    preferences = create_preferences(
                        location=location,
                        budget=budget,
                        cuisines=selected_cuisines,
                        min_rating=min_rating,
                        additional_preferences=additional_preferences if additional_preferences.strip() else None
                    )
                    
                    # Get recommendations
                    response = get_recommendations(preferences, top_k)
                    
                    if response and response.recommendations:
                        st.success(f"Found {len(response.recommendations)} recommendations for you!")
                        
                        # Display summary if available
                        if response.summary:
                            st.info(response.summary)
                        
                        # Display recommendations
                        for i, rec in enumerate(response.recommendations, 1):
                            with st.expander(f"{i}. {rec.name} (Rating: {rec.rating or 'N/A'})"):
                                col_a, col_b = st.columns([2, 1])
                                
                                with col_a:
                                    st.write(f"**Cuisines:** {', '.join(rec.cuisines) if rec.cuisines else 'Various'}")
                                    st.write(f"**Estimated Cost:** {rec.estimated_cost or 'N/A'}")
                                    if rec.score:
                                        st.write(f"**Match Score:** {rec.score:.2f}")
                                
                                with col_b:
                                    if rec.rank:
                                        st.metric("Rank", rec.rank)
                                
                                st.write(f"**Why we recommend this:** {rec.explanation}")
                        
                        # Display metadata
                        st.subheader("Recommendation Details")
                        col_meta1, col_meta2, col_meta3 = st.columns(3)
                        
                        with col_meta1:
                            st.metric("Model Used", response.meta.model)
                        with col_meta2:
                            st.metric("Response Time", f"{response.meta.latency_ms}ms")
                        with col_meta3:
                            st.metric("Dataset Version", response.meta.dataset_version)
                    
                    else:
                        st.warning("No recommendations found. Try adjusting your preferences.")
                        
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
    
    # Footer with additional info
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This AI Restaurant Recommender uses advanced machine learning to provide personalized 
    restaurant recommendations based on your preferences. The system analyzes various factors 
    including cuisine preferences, budget, location, and ratings to suggest the best dining options.
    """)
    
    # Environment info
    if st.session_state.settings:
        with st.expander("Technical Information"):
            st.json({
                "app_name": st.session_state.settings.app_name,
                "environment": st.session_state.settings.environment,
                "llm_provider": st.session_state.settings.llm_provider,
                "llm_model": st.session_state.settings.llm_model,
                "dataset_version": st.session_state.settings.dataset_version
            })

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY environment variable is not set. Please set it to use the AI features.")
        st.stop()
    
    main()
