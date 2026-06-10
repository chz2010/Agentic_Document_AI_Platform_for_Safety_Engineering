from backend.requirements_engineering import build_traceability, extract_requirements_from_text, generate_test_cases


def test_extract_multiline_lidar_requirement_preserves_traceability():
    text = """
    REQ-LIDAR-005: The LiDAR confidence output shall decrease below 0.50 within
    500 ms when point-cloud density, weather degradation, sensor blockage, or ODD
    boundary indicators exceed configured safety thresholds. Linked hazard:
    HZ-LIDAR-004. Linked safety goal: SG-LIDAR-003.

    REQ-LIDAR-007: The LiDAR monitoring function shall detect sensor blockage,
    calibration drift above 0.5 degrees, receiver degradation, and timestamp faults,
    and shall trigger degraded-mode behavior within 1 second. Linked hazard:
    HZ-LIDAR-004. Linked safety goal: SG-LIDAR-003.
    """

    requirements = extract_requirements_from_text(text, "lidar_perception_safety_case.md")

    assert [req.id for req in requirements] == ["REQ-LIDAR-005", "REQ-LIDAR-007"]
    assert requirements[0].linked_hazard == "HZ-LIDAR-004"
    assert requirements[0].linked_safety_goal == "SG-LIDAR-003"
    assert "0.50 within 500 ms" in requirements[0].text
    assert "Linked hazard" not in requirements[0].text
    assert "missing measurable threshold" not in requirements[0].quality_issues
    assert "missing ODD condition" not in requirements[0].quality_issues
    assert "missing linked hazard" not in requirements[0].quality_issues
    assert "missing linked safety goal" not in requirements[0].quality_issues
    assert "within 1 second" in requirements[1].text
    assert requirements[1].linked_hazard == "HZ-LIDAR-004"


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
