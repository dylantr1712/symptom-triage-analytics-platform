from triage_app.extractor import EXTRACTION_SCHEMA


def test_extraction_schema_uses_strict_nested_object_shape():
    raw_evidence = EXTRACTION_SCHEMA["properties"]["raw_evidence"]

    assert raw_evidence["type"] == "object"
    assert raw_evidence["additionalProperties"] is False
    assert set(raw_evidence["properties"]) == {
        "symptoms_text",
        "duration_text",
        "age_text",
        "severity_text",
    }
