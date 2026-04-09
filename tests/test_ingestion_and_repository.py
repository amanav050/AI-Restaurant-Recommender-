from app.data.ingestion import RawRestaurant, normalize
from app.data.repository import FilterCriteria, RestaurantRepository
from app.domain.models import Restaurant


def test_normalize_builds_restaurant_with_budget_band_and_cuisines() -> None:
    raw = RawRestaurant(
        {
            "name": "Test Cafe",
            "location": "Delhi",
            "cuisines_raw": "Italian, Chinese",
            "cost_raw": 500,
            "rating_raw": 4.5,
            "tags_raw": "Casual Dining",
        }
    )

    restaurant = normalize(raw)

    assert restaurant.name == "Test Cafe"
    assert restaurant.location == "Delhi"
    assert set(restaurant.cuisines) == {"Italian", "Chinese"}
    assert restaurant.cost_band == "medium"
    assert restaurant.estimated_cost == 500
    assert restaurant.rating == 4.5
    assert restaurant.tags == ["Casual Dining"]


def test_repository_filter_by_city_and_min_rating() -> None:
    items = [
        Restaurant(
            id="1",
            name="A",
            location="Bangalore",
            cuisines=["Indian"],
            cost_band="low",
            estimated_cost=200,
            rating=3.0,
            tags=[],
        ),
        Restaurant(
            id="2",
            name="B",
            location="Bangalore",
            cuisines=["Italian"],
            cost_band="medium",
            estimated_cost=600,
            rating=4.2,
            tags=[],
        ),
        Restaurant(
            id="3",
            name="C",
            location="Delhi",
            cuisines=["Chinese"],
            cost_band="high",
            estimated_cost=1200,
            rating=4.8,
            tags=[],
        ),
    ]
    repo = RestaurantRepository(items)
    criteria = FilterCriteria(city="Bangalore", min_rating=4.0)

    results = repo.filter(criteria)

    assert len(results) == 1
    assert results[0].id == "2"
