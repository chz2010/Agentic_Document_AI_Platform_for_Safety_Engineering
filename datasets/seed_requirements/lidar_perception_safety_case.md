# Synthetic LiDAR Perception Safety Case

Status: synthetic demo document for requirements extraction, RAG, traceability,
test-case generation, and agent operations monitoring. This is not official
ISO text and is not a replacement for ISO 26262, ISO 21448/SOTIF, ISO 8800, or
an OEM safety case.

## 1. Item Definition

The LiDAR perception item converts point-cloud input into safety-relevant
object, free-space, confidence, tracking, and sensor-health outputs for
downstream fusion, planning, AEB, and automated-driving functions.

Assumed ODD:

- urban and highway roads
- ego speed from 0 km/h to 100 km/h
- daylight, night, light rain, road spray, and partial occlusion
- mounted and calibrated roof or front LiDAR sensor
- downstream consumer uses LiDAR output for collision avoidance and free-space
  planning

## 2. Hazards

- HZ-LIDAR-001: Safety-relevant pedestrian or vehicle is not detected by the
  LiDAR perception function.
- HZ-LIDAR-002: Object distance or relative velocity is overestimated, causing
  late braking or unsafe planning.
- HZ-LIDAR-003: Occupied space is incorrectly reported as free space.
- HZ-LIDAR-004: LiDAR confidence remains high during degraded visibility,
  sparse point clouds, sensor blockage, or ODD boundary conditions.
- HZ-LIDAR-005: Stale point-cloud data is accepted as current by downstream
  fusion or planning.

## 3. Safety Goals

- SG-LIDAR-001: Prevent missing safety-relevant objects when LiDAR perception
  is required for collision avoidance.
- SG-LIDAR-002: Prevent unsafe vehicle behavior caused by wrong LiDAR range,
  velocity, or free-space output.
- SG-LIDAR-003: Prevent downstream overtrust in degraded or uncertain LiDAR
  perception output.
- SG-LIDAR-004: Ensure stale, invalid, or delayed point-cloud data is rejected
  before it can influence safety-relevant decisions.

## 4. Candidate Requirements

REQ-LIDAR-001: The LiDAR perception system shall detect safety-relevant
pedestrians and vehicles within 45 m at ego speeds up to 50 km/h in the active
ODD and verify detection performance using scenario test evidence. Linked
hazard: HZ-LIDAR-001. Linked safety goal: SG-LIDAR-001.

REQ-LIDAR-002: The LiDAR perception system shall estimate object distance with
an absolute error below 0.5 m for safety-relevant objects within 30 m and verify
the result using calibrated ground-truth measurement evidence. Linked hazard:
HZ-LIDAR-002. Linked safety goal: SG-LIDAR-002.

REQ-LIDAR-003: The LiDAR perception system shall estimate relative velocity
with an error below 1.0 m/s for tracked safety-relevant objects and validate the
result across cut-in, lead-vehicle braking, and pedestrian crossing scenarios.
Linked hazard: HZ-LIDAR-002. Linked safety goal: SG-LIDAR-002.

REQ-LIDAR-004: The LiDAR free-space module shall mark occupied regions as
non-drivable when obstacle confidence is above 0.70 and shall verify this
behavior in construction-zone, road-edge, and static-obstacle scenarios. Linked
hazard: HZ-LIDAR-003. Linked safety goal: SG-LIDAR-002.

REQ-LIDAR-005: The LiDAR confidence output shall decrease below 0.50 within
500 ms when point-cloud density, weather degradation, sensor blockage, or ODD
boundary indicators exceed configured safety thresholds. Linked hazard:
HZ-LIDAR-004. Linked safety goal: SG-LIDAR-003.

REQ-LIDAR-006: The perception interface shall invalidate LiDAR object and
free-space outputs when point-cloud age exceeds 100 ms or when frame sequence
counters indicate dropped data, and shall verify invalidation using fault
injection tests. Linked hazard: HZ-LIDAR-005. Linked safety goal:
SG-LIDAR-004.

REQ-LIDAR-007: The LiDAR monitoring function shall detect sensor blockage,
calibration drift above 0.5 degrees, receiver degradation, and timestamp faults,
and shall trigger degraded-mode behavior within 1 second. Linked hazard:
HZ-LIDAR-004. Linked safety goal: SG-LIDAR-003.

REQ-LIDAR-008: The LiDAR validation dataset shall include at least 3,000
labeled safety-relevant object samples across night, rain, spray, occlusion,
low-reflectivity objects, and sparse point-cloud conditions. Linked hazard:
HZ-LIDAR-001. Linked safety goal: SG-LIDAR-001.

REQ-LIDAR-009: The LiDAR model release process shall block deployment when any
safety KPI regresses by more than 2 percent on protected validation scenarios
or when uncertainty calibration exceeds the approved error bound. Linked
hazard: HZ-LIDAR-004. Linked safety goal: SG-LIDAR-003.

REQ-LIDAR-010: The downstream planner shall treat unknown or low-confidence
LiDAR objects as safety-relevant obstacles until sensor fusion or additional
evidence resolves the uncertainty. Linked hazard: HZ-LIDAR-004. Linked safety
goal: SG-LIDAR-003.

## 5. Weak Requirements For Quality Review

REQ-LIDAR-WEAK-001: The LiDAR system shall be robust in difficult weather.

REQ-LIDAR-WEAK-002: The perception system should quickly detect objects when
needed.

REQ-LIDAR-WEAK-003: The AI model shall perform well for unusual scenarios.

## 6. Evidence Sources

- EV-LIDAR-001: Scenario validation report for night pedestrian crossing,
  partial occlusion, and low-reflectivity clothing.
- EV-LIDAR-002: Fault injection report for stale point cloud, dropped frame,
  calibration offset, CRC error, and frozen track.
- EV-LIDAR-003: Dataset coverage matrix for LiDAR point-cloud scenarios by
  ODD, object class, weather, visibility, and occlusion.
- EV-LIDAR-004: Confidence calibration report for sparse point clouds, rain,
  sensor blockage, and unknown objects.

## 7. Test Cases

- TC-LIDAR-NIGHT-PED-001: Verify detection of a partially occluded pedestrian
  at night within 45 m and below 50 km/h.
- TC-LIDAR-RANGE-001: Verify LiDAR range error below 0.5 m for static and
  moving objects within 30 m.
- TC-LIDAR-FREESPACE-001: Verify occupied-space rejection in construction-zone
  and road-edge scenes.
- TC-LIDAR-STALE-DATA-001: Inject stale point-cloud frames and verify output
  invalidation within 100 ms.
- TC-LIDAR-BLOCKAGE-001: Simulate sensor blockage and verify confidence
  degradation and degraded-mode trigger within 1 second.

## 8. Review Notes

The strong requirements include measurable thresholds, ODD conditions, linked
hazards, linked safety goals, and verification methods. The weak requirements
are intentionally vague so the quality scoring module can identify missing
measurability, missing ODD context, missing verification methods, and weak
traceability.
