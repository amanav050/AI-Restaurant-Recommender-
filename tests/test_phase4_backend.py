from app.domain.models import Restaurant
from app.services.merger import Merger
from app.services.response_parser import RankedOutput, ResponseParser


def test_response_parser_handles_markdown_fences() -> None:
    text = """```json
    {"items":[{"restaurant_id":"r1","explanation":"Because."}],"summary":"ok"}
    ```"""
    parsed = ResponseParser.parse(text)
    assert parsed.summary == "ok"
    assert parsed.items[0].restaurant_id == "r1"


def test_merger_validates_allowed_ids_and_merges() -> None:
    candidates = [
        Restaurant(id="r1", name="A", location="BTM"),
        Restaurant(id="r2", name="B", location="BTM"),
    ]
    ranked = RankedOutput.model_validate(
        {
            "items": [
                {"restaurant_id": "r2", "explanation": "match"},
                {"restaurant_id": "nope", "explanation": "x"},
            ]
        }
    )
    items, _ = Merger.merge(candidates=candidates, ranked=ranked, allowed_ids={"r1", "r2"}, top_k=2)
    assert len(items) == 1
    assert items[0].restaurant_id == "r2"

