import pytest

from triage_app.extractor import StubExtractionClient, SymptomExtractor


class BrokenClient:
    def extract_json(self, prompt: str, user_text: str) -> str:
        return "not-json"


def test_stub_extractor_returns_strict_payload():
    extractor = SymptomExtractor(StubExtractionClient())

    result = extractor.extract(
        "I am 42 and I have had severe chest pain and shortness of breath since this morning."
    )

    assert result.payload.symptoms == ["chest_pain", "shortness_of_breath"]
    assert result.payload.duration_bucket == "hours"
    assert result.payload.age_years == 42
    assert result.payload.severity_cues == ["severe"]


def test_extractor_rejects_non_json_response():
    extractor = SymptomExtractor(BrokenClient())

    with pytest.raises(ValueError):
        extractor.extract("hello")
