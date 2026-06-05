# Automotive Safety Requirements Seed Dataset

## Hazards

- HZ-AEB-001: The vehicle fails to detect a pedestrian crossing the ego lane at night, causing late or missing automatic emergency braking.
- HZ-LKA-001: The vehicle unintentionally departs its lane because the driver does not receive a timely warning.
- HZ-LKA-002: Lane marking confidence degrades silently, causing the lane keeping function to remain active without reliable perception.
- HZ-PER-001: The perception system misses vulnerable road users under adverse visibility or occlusion conditions.
- HZ-MRM-001: The vehicle continues automated operation after perception becomes unavailable.
- HZ-MON-001: Safety-relevant interventions cannot be audited because runtime event data is missing.

## Safety Goals

- SG-AEB-001: Avoid or mitigate collision with pedestrians within the defined AEB operational design domain.
- SG-LKA-001: Warn the driver early enough to prevent unintended lane departure on marked roads.
- SG-LKA-002: Deactivate or degrade gracefully when lane confidence is not sufficient for safe lane keeping.
- SG-PER-001: Maintain traceable perception coverage for vulnerable road user detection across relevant ODD conditions.
- SG-MRM-001: Bring the vehicle to a safe stop when automated operation can no longer rely on object detection.
- SG-MON-001: Preserve objective evidence for safety-relevant runtime interventions.

## Requirements

REQ-AEB-001: The AEB pedestrian system shall detect partially occluded pedestrians at night within 40 m for ego vehicle speeds up to 50 km/h and verify the result by scenario test evidence. Linked hazard: HZ-AEB-001. Linked safety goal: SG-AEB-001.

REQ-AEB-002: The AEB validation campaign shall include at least 30 night-time pedestrian crossing scenarios with low-beam headlights, wet road surface, and measured illumination below 10 lux. Linked hazard: HZ-AEB-001. Linked safety goal: SG-AEB-001.

REQ-AEB-003: The AEB system shall react quickly when a pedestrian is detected in front of the vehicle. Linked hazard: HZ-AEB-001. Linked safety goal: SG-AEB-001.

REQ-LKA-001: The lane keeping assist system shall warn the driver within 500 ms when unintended lane departure risk is detected at speeds between 60 km/h and 130 km/h on clearly marked roads. Linked hazard: HZ-LKA-001. Linked safety goal: SG-LKA-001.

REQ-LKA-002: The system shall monitor lane marking confidence at runtime and record a diagnostic event when confidence remains below 70% for more than 2 seconds. Linked hazard: HZ-LKA-002. Linked safety goal: SG-LKA-002.

REQ-PER-001: The perception dataset shall include at least 5,000 labeled vulnerable road user samples across night, rain, glare, and partial occlusion conditions. Linked hazard: HZ-PER-001. Linked safety goal: SG-PER-001.

REQ-PER-002: The perception software shall publish object detection confidence, object class, bounding box, timestamp, and sensor source for every tracked vulnerable road user at a minimum rate of 10 Hz. Linked hazard: HZ-PER-001. Linked safety goal: SG-PER-001.

REQ-MRM-001: The minimal risk maneuver controller shall transition the vehicle to a safe stop within 8 seconds when the perception subsystem reports unavailable object detection for more than 1 second in the active ODD. Linked hazard: HZ-MRM-001. Linked safety goal: SG-MRM-001.

REQ-EVI-001: Each safety requirement shall be linked to one hazard, one safety goal, one verification method, and at least one objective evidence artifact before release approval.

REQ-MON-001: The deployed system shall store safety monitor events with timestamp, vehicle speed, ODD state, triggering condition, and software version for 100% of safety-relevant interventions. Linked hazard: HZ-MON-001. Linked safety goal: SG-MON-001.

## Traceability Examples

hazard_id,hazard_description,safety_goal_id,requirement_id,test_case_id,status
HZ-AEB-001,Night-time pedestrian collision risk,SG-AEB-001,REQ-AEB-001,TC-AEB-NIGHT-OCCLUSION-001,ready_for_review
HZ-AEB-001,Night-time pedestrian collision risk,SG-AEB-001,REQ-AEB-002,TC-AEB-NIGHT-OCCLUSION-002,ready_for_review
HZ-LKA-001,Lane departure warning delay,SG-LKA-001,REQ-LKA-001,TC-LKA-DEPARTURE-001,ready_for_review
HZ-PER-001,Missing vulnerable road users,SG-PER-001,REQ-PER-001,TC-PER-DATASET-COVERAGE-001,needs_review
HZ-MRM-001,Continued operation after perception loss,SG-MRM-001,REQ-MRM-001,TC-MRM-SAFE-STOP-001,needs_review

## Test Case Examples

- TC-AEB-NIGHT-OCCLUSION-001: Execute a night-time pedestrian crossing scenario with partial occlusion, ego speed up to 50 km/h, and measured detection distance. Pass only if detection occurs within the required range and evidence is recorded.
- TC-LKA-DEPARTURE-001: Execute lane departure scenarios between 60 km/h and 130 km/h on marked roads. Pass only if the driver warning occurs within 500 ms.
- TC-PER-DATASET-COVERAGE-001: Audit dataset labels and scenario metadata. Pass only if coverage counts satisfy the required night, rain, glare, and occlusion conditions.
