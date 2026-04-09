import pytest

from app.core.config import get_settings
from app.data.repository import FilterCriteria, RestaurantRepository
from app.domain.models import UserPreferences
from app.services.groq_client import GroqLlmClient
from app.services.recommendation import RecommendationService


def _has_groq_key() -> bool:
    return bool(get_settings().effective_llm_api_key)


@pytest.mark.integration
def test_groq_client_basic_completion() -> None:
    if not _has_groq_key():
        pytest.skip("Groq API key not set in environment (.env).")

    settings = get_settings()
    client = GroqLlmClient(settings)
    result = client.complete(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": "Return only the word OK."},
            {"role": "user", "content": "Say OK."},
        ],
        temperature=0.0,
    )
    assert "OK" in result.content


@pytest.mark.integration
def test_end_to_end_recommendations_are_grounded() -> None:
    if not _has_groq_key():
        pytest.skip("Groq API key not set in environment (.env).")

    repo = RestaurantRepository.from_parquet()
    service = RecommendationService(repo)

    prefs = UserPreferences(
        location="BTM",
        budget="medium",
        cuisines=[],
        min_rating=4.2,
        additional_preferences="Quick service, good ambiance, not too expensive.",
    )
    response = service.recommend(prefs, top_k=3)

    assert 1 <= len(response.recommendations) <= 3
    ids = [r.restaurant_id for r in response.recommendations]
    assert len(ids) == len(set(ids))
    for rec in response.recommendations:
        assert rec.explanation.strip()


@pytest.mark.integration
def test_recommendations_respect_candidate_list_ids() -> None:
    if not _has_groq_key():
        pytest.skip("Groq API key not set in environment (.env).")

    repo = RestaurantRepository.from_parquet()
    service = RecommendationService(repo)

    prefs = UserPreferences(
        location="HSR",
        budget="low",
        cuisines=[],
        min_rating=4.0,
        additional_preferences="Family-friendly and calm.",
    )
    response = service.recommend(prefs, top_k=3)

    allowed_ids = {
        r.id
        for r in repo.filter(
            FilterCriteria(city=prefs.location, min_rating=float(prefs.min_rating))
        )
    }
    for rec in response.recommendations:
        assert rec.restaurant_id in allowed_ids

