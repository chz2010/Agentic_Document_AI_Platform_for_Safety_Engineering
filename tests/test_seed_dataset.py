from backend.seed_data import load_seed_requirements, seed_document_text


def test_seed_requirements_load_with_quality_scores():
    requirements = load_seed_requirements()

    assert len(requirements) == 10
    assert requirements[0].id == "REQ-AEB-001"
    assert requirements[0].linked_hazard == "HZ-AEB-001"
    assert requirements[0].quality_score > 0.75
    assert "too vague" in next(req for req in requirements if req.id == "REQ-AEB-003").quality_issues


def test_seed_document_contains_traceability_examples():
    text = seed_document_text()

    assert "## Traceability Examples" in text
    assert "TC-AEB-NIGHT-OCCLUSION-001" in text
