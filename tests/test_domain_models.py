from app.domain.models import (
    RecommendationMeta,
    RecommendationResponse,
    Restaurant,
    UserPreferences,
)


def test_restaurant_model_shape() -> None:
    row = Restaurant(
        id="r1",
        name="Sample Bistro",
        location="Bangalore",
        cuisines=["Italian"],
        cost_band="medium",
        rating=4.2,
    )
    assert row.name == "Sample Bistro"
    assert row.cost_band == "medium"


def test_user_preferences_validation() -> None:
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisines=["Indian", "Chinese"],
        min_rating=3.5,
    )
    assert prefs.budget == "low"
    assert len(prefs.cuisines) == 2


def test_recommendation_response_contract() -> None:
    response = RecommendationResponse(
        recommendations=[],
        meta=RecommendationMeta(model="mock-model", latency_ms=10, dataset_version="v1"),
    )
    assert response.meta.model == "mock-model"
