from backend.requirements_engineering import build_traceability, extract_requirements_from_text, generate_test_cases


def test_extract_requirements_scores_quality_gaps():
    text = """
    REQ-AEB-001: The AEB pedestrian system shall detect partially occluded pedestrians at night.
    REQ-AEB-002: The system shall validate pedestrian detection within 40 m at speeds below 50 km/h and store test evidence.
    """

    requirements = extract_requirements_from_text(text, "aeb_safety_case.md")

    assert len(requirements) == 2
    assert requirements[0].id == "REQ-AEB-001"
    assert "missing measurable threshold" in requirements[0].quality_issues
    assert requirements[1].quality_score > requirements[0].quality_score


def test_traceability_and_test_case_generation():
    requirements = extract_requirements_from_text(
        "REQ-AEB-003: The system shall verify HZ-AEB-001 and SG-AEB-001 by test within 30 m at night.",
        "test_plan.md",
    )

    traceability = build_traceability(requirements)
    test_cases = generate_test_cases(requirements)

    assert traceability[0].hazard_id == "HZ-AEB-001"
    assert traceability[0].safety_goal_id == "SG-AEB-001"
    assert test_cases[0].linked_requirement == "REQ-AEB-003"

