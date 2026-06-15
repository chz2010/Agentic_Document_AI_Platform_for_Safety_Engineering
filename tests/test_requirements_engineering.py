from backend.requirements_engineering import build_traceability, extract_requirements_from_text, generate_test_cases


def test_extract_multiline_lidar_requirement_preserves_traceability():
    text = """
    REQ-LIDAR-005: The LiDAR confidence output shall decrease below 0.50 within
    500 ms when point-cloud density, weather degradation, sensor blockage, or ODD
    boundary indicators exceed configured safety thresholds and shall be verified
    by scenario test evidence. Linked hazard: HZ-LIDAR-004. Linked safety goal:
    SG-LIDAR-003.

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


def test_good_lidar_requirement_suggests_missing_test_case_link():
    text = """
    REQ-LIDAR-005: The LiDAR confidence output shall decrease below 0.50 within
    500 ms when point-cloud density, weather degradation, sensor blockage, or ODD
    boundary indicators exceed configured safety thresholds and shall be verified
    by scenario test evidence. Linked hazard: HZ-LIDAR-004. Linked safety goal:
    SG-LIDAR-003.
    """

    requirements = extract_requirements_from_text(text, "lidar_perception_safety_case.md")

    assert requirements[0].quality_issues == []
    assert requirements[0].linked_test_cases == []
    assert requirements[0].suggested_improvement == (
        "Link this requirement to at least one verification test case with scenario, "
        "pass/fail criteria, and required evidence."
    )


def test_extract_requirement_preserves_linked_test_case_metadata():
    text = """
    REQ-LIDAR-006: The LiDAR perception monitor shall verify blockage detection
    within 250 ms in rain and fog ODD conditions. Linked hazard: HZ-LIDAR-004.
    Linked safety goal: SG-LIDAR-003. Linked test case: TC-LIDAR-BLOCKAGE-001.
    """

    requirements = extract_requirements_from_text(text, "lidar_perception_safety_case.md")

    assert requirements[0].linked_test_cases == ["TC-LIDAR-BLOCKAGE-001"]
    assert "Linked test case" not in requirements[0].text
    assert "verification test case" not in (requirements[0].suggested_improvement or "")


def test_extract_links_from_new_document_id_scheme():
    text = """
    SYS-REQ-17: The door controller shall unlock within 300 ms during emergency
    evacuation mode and shall be verified by integration test evidence. Hazard ID:
    H-17. Safety objective: SO-3. Verification case: TEST-04.
    """

    requirements = extract_requirements_from_text(text, "rail_door_controller_spec.md")

    assert requirements[0].id == "SYS-REQ-17"
    assert requirements[0].linked_hazard == "H-17"
    assert requirements[0].linked_safety_goal == "SO-3"
    assert requirements[0].linked_test_cases == ["TEST-04"]
    assert "Hazard ID" not in requirements[0].text
    assert requirements[0].suggested_improvement is None


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
