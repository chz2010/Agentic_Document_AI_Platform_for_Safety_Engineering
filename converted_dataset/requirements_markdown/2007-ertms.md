# ERTMS/ETCS Functional Requirements Specification FRS

- Source file: `2007-ertms.xml`
- Version: 5.00
- Issue date: 2007-06-21
- File number: ERA/ERTMS/003204

## 1 Introduction

### 1.1

This document defines the functional requirements for ERTMS/ETCS (EUROPEAN RAIL TRAFFIC MANAGEMENT SYSTEM / EUROPEAN TRAIN CONTROL SYSTEM). The document primarily defines the operational requirements and therefore contains only a few technical terms. For consistency reasons, all functional requirements not implemented in the SRS 2.3.0 have been removed from this version.

### 1.5

In the requirements of this document: (M) = Mandatory:The requirement shall be respected in every ETCS application. The applicable requirements stated in ETCS SRS and lower level mandatory specifications shall be respected. (O) = Optional:It is not mandatory to implement this function in every ETCS application. If implemented, the applicable requirements stated in ETCS SRS and lower level mandatory specifications shall be respected. Note that the CCS TSI may define specific conditions, where implementation of O functions may be required for safety reasons.

## 3 General requirements

### 3.1 Basic functioning

## Requirement 3.1.1.1a

REQ-2007-ERTMS-3.1.1.1a: ETCS shall provide the driver with information to allow him to drive the train safely.

## Requirement 3.1.1.1b

REQ-2007-ERTMS-3.1.1.1b: ETCS shall be able to supervise train and shunting movements.

## Requirement 3.1.1.1c

REQ-2007-ERTMS-3.1.1.1c: If the supervision is performed by a RBC it shall be possible to prevent movements of a traction unit in its area if not authorised by the RBC.

## Requirement 3.1.1.10

REQ-2007-ERTMS-3.1.1.10: ETCS is required to be functional to a maximum train speed of 500 km/h.

### 3.2 Application levels

## Requirement 3.2.1.3a

REQ-2007-ERTMS-3.2.1.3a: The following definitions shall apply for the ETCS application levels: Level 0: ETCS active for limited train control function; trackside not fitted with any train control system or fitted with a train control system for which no STM is available onboard. Level 1: Basic track to train information via intermittent transmission media, e.g. balises. This information can be supported by infill, transmitted via balise, loop or radio. Level 2: Basic track to train and train to track information via continuous transmission media, i.e. radio. The train detection is provided by trackside. Level 3: Same as level 2 except that train integrity is provided by onboard and therefore trackside. train detection is optional. Level STM (Specific Transmission Module): Track to train information provided by national system. Onboard functions provided by national system (STM) in co-operation with onboard ETCS.

## Requirement 3.2.1.3b

REQ-2007-ERTMS-3.2.1.3b: It shall be possible to implement one or more of the ETCS application levels on a line.

## Requirement 3.2.1.3c

REQ-2007-ERTMS-3.2.1.3c: Trains equipped for ERTMS/ETCS application level 3 shall be able to run on lines equipped with ERTMS/ETCS application level 3, 2, 1 and 0, trains equipped for ERTMS/ETCS application level 2 shall be able to run on lines equipped with ERTMS/ETCS application level 2, 1 and 0 and trains equipped for ERTMS/ETCS application level 1 shall be able to run on lines equipped with ERTMS/ETCS application level 1 and 0.

## Requirement 3.2.1.3d

REQ-2007-ERTMS-3.2.1.3d: The current application level shall be indicated on the DMI.

## Requirement 3.2.1.5

REQ-2007-ERTMS-3.2.1.5: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledge after the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released

### 3.7 Operation with existing national train control systems

## Requirement 3.7.1.1

REQ-2007-ERTMS-3.7.1.1: ETCS shall be compatible with existing national systems listed in the CCS TSI such that it does not interfere with the national systems and is not interfered with by the national systems.

### 3.9 Operational states

## Requirement 3.9.1.1

REQ-2007-ERTMS-3.9.1.1: The ETCS trainborne equipment shall be capable of supervising the following operational states: Full Supervision operation Partial Supervision operation Staff Responsible operation On Sight operation Unfitted Line operation Train Trip operation Post Trip operation National operation (STM) Tandem operation Multiple operation Shunting operation Stand By operation Reversing operation

## Requirement 3.9.1.2a

REQ-2007-ERTMS-3.9.1.2a: Any transition which occurs while the train is moving shall in principle occur automatically.

## Requirement 3.9.1.2b

REQ-2007-ERTMS-3.9.1.2b: Transitions which occur while the train is stationary, shall be initiated automatically or manually as appropriate.

## Requirement 3.9.1.2c

REQ-2007-ERTMS-3.9.1.2c: If, as a result of an automatic transition, except for transitions to and from National Operation (STM), the responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether the train is stationary or not.

## Requirement 3.9.1.2d

REQ-2007-ERTMS-3.9.1.2d: For transitions to and from National Operation (STM) the ETCS shall request, an acknowledgement by the driver.

## Requirement 3.9.1.2e

REQ-2007-ERTMS-3.9.1.2e: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shall initiate a brake application

## Requirement 3.9.1.3

REQ-2007-ERTMS-3.9.1.3: During the transition period between two operational states (including two different national operations) the supervision provided shall at least ensure the same protection provided by the least restrictive state.

## Requirement 3.9.1.4

REQ-2007-ERTMS-3.9.1.4: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shall switch to the highest level, according to the priority given by trackside, for which it is equipped.

## Requirement 3.9.1.5

REQ-2007-ERTMS-3.9.1.5: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shall initiate a brake application.

## Requirement 3.9.1.6

REQ-2007-ERTMS-3.9.1.6: The current operational status shall be indicated to the driver on the DMI

### 3.10 National values

## Requirement 3.10.1.1

REQ-2007-ERTMS-3.10.1.1: The ETCS on-board shall be capable of receiving National values from the trackside to adapt to National requirements

## Requirement 3.10.1.3

REQ-2007-ERTMS-3.10.1.3: National values shall be applicable to a defined area

## Requirement 3.10.1.6

REQ-2007-ERTMS-3.10.1.6: Once received onboard the national values shall remain valid even if the onboard equipment is switched off

### 3.11 Default values for the national values

## Requirement 3.10.1.1

REQ-2007-ERTMS-3.10.1.1: If the on-board has no valid national values for the current location, default values shall be used by the onboard equipment.

## Requirement 3.10.1.2

REQ-2007-ERTMS-3.10.1.2: Default values shall be harmonised values, permanently stored in all ERTMS/ETCS on board equipment

## 4 Functions

### 4.1 Operational Functions

#### 4.1.1 On Board Equipment self Test

## Requirement 4.1.1.3a

REQ-2007-ERTMS-4.1.1.3a: At Start Up, the on board equipment shall perform an automatic self-test.

## Requirement 4.1.1.4b

REQ-2007-ERTMS-4.1.1.4b: The test shall require no action on the part of the driver.

## Requirement 4.1.1.4c

REQ-2007-ERTMS-4.1.1.4c: The DMI shall indicate the result of the self-test.

#### 4.1.2 Train and driver Data Entry

## Requirement 4.1.2.1a

REQ-2007-ERTMS-4.1.2.1a: Train data shall be entered before the on-board ETCS equipment allows train movement.

## Requirement 4.1.2.2

REQ-2007-ERTMS-4.1.2.2: The driver shall be able to select Train Data Entry on the DMI.

## Requirement 4.1.2.3a

REQ-2007-ERTMS-4.1.2.3a: Entering or overwriting data manually by the driver shall be possible but only when stationary.

## Requirement 4.1.2.5a

REQ-2007-ERTMS-4.1.2.5a: Train data may be entered automatically from a railway management system or from train memory.

## Requirement 4.1.2.9

REQ-2007-ERTMS-4.1.2.9: The driver shall be able to consult train data when the train is stationary or moving.

## Requirement 4.1.2.10

REQ-2007-ERTMS-4.1.2.10: Current train data shall be stored (except at transition to shunting) in the ETCS equipment until the traction unit is not operative.

## Requirement 4.1.2.11

REQ-2007-ERTMS-4.1.2.11: Stored train data shall be offered to the driver to be confirmed when Data Entry starts.

## Requirement 4.1.2.13

REQ-2007-ERTMS-4.1.2.13: The system for Train Data Entry shall provide for the input of other data required by STMs connected to ETCS. This may require additional items, not required for ETCS, to be entered.

## Requirement 4.1.2.14a

REQ-2007-ERTMS-4.1.2.14a: The entry of driver identification and the selection of the language shall be possible.

## Requirement 4.1.2.14b

REQ-2007-ERTMS-4.1.2.14b: The change of driver identification during a journey or a Train Running Number shall be possible

## Requirement 4.1.2.15

REQ-2007-ERTMS-4.1.2.15: Following successful completion of Train Data Entry, the driver shall be able to perform shunting movements or train movements.

## Requirement 4.1.2.16

REQ-2007-ERTMS-4.1.2.16: The following data may be entered manually by the driver or from train memory: Driver identification Train identification (train number) STM ready for use Data required for brake calculation Maximum train speed Train length Status of air tight system Type of electric power accepted Data additional required for STM (if any) International train category Train gauge Maximum axle load of the train with a resolution of 0,5 t

## Requirement 4.1.2.16

REQ-2007-ERTMS-4.1.2.16: The following data may be entered manually by the driver provided by external sources : Driver identification Train identification (train number) STM ready for use Data required for brake calculation Maximum train speed Train length Status of air tight system Type of electric power accepted Data additional required for STM (if any) International train category Train gauge Maximum axle load of the train with a resolution of 0,5 t

## Requirement 4.1.2.17

REQ-2007-ERTMS-4.1.2.17: If the onboard fails to contact the RBC when awakening the driver shall be asked to enter the RBC contact details

#### 4.1.3 Shunting operation

## Requirement 4.1.3.1

REQ-2007-ERTMS-4.1.3.1: An ETCS equipped traction unit shall be capable of being moved in Shunting without train data, track data or movement authority.

## Requirement 4.1.3.2a

REQ-2007-ERTMS-4.1.3.2a: Transfer to Shunting on driver’s selection shall only be possible when stationary.

## Requirement 4.1.3.2c

REQ-2007-ERTMS-4.1.3.2c: To prevent unauthorised use of the function permission shall be obtained from the RBC if the train is operating under the control of the RBC.

## Requirement 4.1.3.2d

REQ-2007-ERTMS-4.1.3.2d: Permission received shall be indicated to the driver.

## Requirement 4.1.3.3

REQ-2007-ERTMS-4.1.3.3: It shall be possible to manually select Shunting from Stand By operation, Full Supervision operation or Partial Supervision operation

## Requirement 4.1.3.4a

REQ-2007-ERTMS-4.1.3.4a: Automatic transfer to Shunting may be from Full Supervision operation and Partial Supervision operation status at any speed lower than or equal to the supervised shunting speed based on trackside information.

## Requirement 4.1.3.4b

REQ-2007-ERTMS-4.1.3.4b: Before authomatic transition to Shunting, ETCS shall request confirmation from the driver.

## Requirement 4.1.3.5a

REQ-2007-ERTMS-4.1.3.5a: ETCS shall supervise Shunting operation to a permitted national speed value.

## Requirement 4.1.3.5b

REQ-2007-ERTMS-4.1.3.5b: The supervised Shunting speed shall be indicated to the driver on request.

## Requirement 4.1.3.6

REQ-2007-ERTMS-4.1.3.6: It shall be possible to apply the train trip function, if the shunting movement passes a signal showing "danger for shunting".

## Requirement 4.1.3.8a

REQ-2007-ERTMS-4.1.3.8a: Exit from Shunting shall only be possible when the train is stationary.

## Requirement 4.1.3.8b

REQ-2007-ERTMS-4.1.3.8b: Exit from Shunting shall take place when the driver selects exit from shunting.

#### 4.1.4 Partial Supervision

## Requirement 4.1.4.1

REQ-2007-ERTMS-4.1.4.1: Partial Supervision shall be selected either by the Driver, or by information received from track-to-train transmission.

## Requirement 4.1.4.2a

REQ-2007-ERTMS-4.1.4.2a: If acknowledgement is specified the driver shall acknowledge transfer from Full Supervision to Partial Supervision within 5 seconds

## Requirement 4.1.4.3

REQ-2007-ERTMS-4.1.4.3: Partial Supervision shall be indicated on the DMI.

## Requirement 4.1.4.4a

REQ-2007-ERTMS-4.1.4.4a: In Partial Supervision the train shall be supervised according to train speed and distance data available.

## Requirement 4.1.4.4b

REQ-2007-ERTMS-4.1.4.4b: The train shall have the capability of being supervised to a ceiling speed.

## Requirement 4.1.4.4c

REQ-2007-ERTMS-4.1.4.4c: This ceiling speed shall not be shown continually on the DMI but may be shown momentarily when selected by the driver.

## Requirement 4.1.4.6

REQ-2007-ERTMS-4.1.4.6: The train shall leave Partial Supervision when the trainborne equipment is not operative any longer, when Shunting is selected or when Full Supervision is available.

## Requirement 4.1.4.7

REQ-2007-ERTMS-4.1.4.7: It shall be possible to order a train trip when passing a stop signal

#### 4.1.5 Full Supervision operation

## Requirement 4.1.5.1a

REQ-2007-ERTMS-4.1.5.1a: Transferring to Full Supervision shall occur automatically when a movement authority and all other necessary information is received through track-to-train transmission.

## Requirement 4.1.5.1b

REQ-2007-ERTMS-4.1.5.1b: It shall be possible for the trackside to ask a driver for confirmation about the occupancy of the track ahead before sending a Full Supervision movement authority.

## Requirement 4.1.5.4

REQ-2007-ERTMS-4.1.5.4: Full Supervision shall provide supervision of speed and distance.

## Requirement 4.1.5.5

REQ-2007-ERTMS-4.1.5.5: The trainborne equipment shall remain in Full Supervision until the trainborne equipment is not active any longer, when Shunting is selected or when Partial Supervision information is received.

#### 4.1.6 Isolation of ETCS trainborne equipment

## Requirement 4.1.6.1a

REQ-2007-ERTMS-4.1.6.1a: The ETCS trainborne equipment shall be capable of being isolated.

## Requirement 4.1.6.5

REQ-2007-ERTMS-4.1.6.5: When the ETCS trainborne equipment is isolated, the system shall not show any ETCS information other than the fact that the system is isolated.

## Requirement 4.1.6.6

REQ-2007-ERTMS-4.1.6.6: Isolation of the ETCS trainborne equipment shall disconnect the ETCS trainborne equipment from the vehicle braking system.

#### 4.1.7 Compatibility with existing train control and protection systems

## Requirement 4.1.7.1

REQ-2007-ERTMS-4.1.7.1: The ETCS trainborne equipment shall be capable of receiving information from the national train control systems by means of the STM.

## Requirement 4.1.7.2

REQ-2007-ERTMS-4.1.7.2: The DMI shall display or be compatible with information from national train control systems. This may mean displaying the information shown by the national system.

#### 4.1.8 Unfitted Line Operation

## Requirement 4.1.8.1

REQ-2007-ERTMS-4.1.8.1: Unfitted operation shall be possible if ordered by trackside

## Requirement 4.1.8.2

REQ-2007-ERTMS-4.1.8.2: Unfitted operation shall be possible if selected by the driver at start up

## Requirement 4.1.8.3

REQ-2007-ERTMS-4.1.8.3: The on board shall supervise the train against a ceiling speed

## Requirement 4.1.8.4

REQ-2007-ERTMS-4.1.8.4: The ceiling speed value for the unfitted operation is determined by the lower value out of Maximum train speed National value for unfitted operation

## Requirement 4.1.8.5

REQ-2007-ERTMS-4.1.8.5: The onboard shall be capable to switch to another ETCS status when transmitted from trackside

### 4.2 Infrastructure Functions

#### 4.2.1

## Requirement 4.1.1.1

REQ-2007-ERTMS-4.1.1.1: The ETCS on-board shall be capable of receiving track description from the trackside.

## Requirement 4.1.1.3a

REQ-2007-ERTMS-4.1.1.3a: It shall be possible to send information on adhesion conditions from trackside.

## Requirement 4.1.1.3b

REQ-2007-ERTMS-4.1.1.3b: It shall also be possible, to allow the driver to change the adhesion conditions; in this case information from trackside has priority.

## Requirement 4.1.1.4a

REQ-2007-ERTMS-4.1.1.4a: The trackside shall be able to send information for the calculation of speed profiles.

## Requirement 4.1.1.4b

REQ-2007-ERTMS-4.1.1.4b: If track data at least to the location where the relevant movement authority ends are not available on-board, the movement authority shall be rejected.

## Requirement 4.1.1.5

REQ-2007-ERTMS-4.1.1.5: Track to train transmission shall provide the capability to send different speed profiles for specific train categories.

#### 4.2.2 End of movement authority

## Requirement 4.2.2.1

REQ-2007-ERTMS-4.2.2.1: The ETCS trainborne equipment shall supervise the end of movement authority, if this information is available on-board.

## Requirement 4.2.2.2

REQ-2007-ERTMS-4.2.2.2: The target distance to be displayed on the DMI shall be based on the most restrictive braking curve.

## Requirement 4.2.2.3

REQ-2007-ERTMS-4.2.2.3: Together with the movement authority, the on board shall be able to receive one or more time-out(s) for certain sections of the movement authority, and shorten the movement authority accordingly when a time out expires.

#### 4.2.3 Supervision of driving into a section of track which could be occupied (On Sight operation)

## Requirement 4.2.3.1

REQ-2007-ERTMS-4.2.3.1: Using train data and infrastructure data, braking curves shall be calculated taking into account the target information but not the location of vehicles occupying the track.

## Requirement 4.2.3.2

REQ-2007-ERTMS-4.2.3.2: The ceiling speed level for the movement authority shall be defined as data National Value.

## Requirement 4.2.3.4

REQ-2007-ERTMS-4.2.3.4: Before entering an occupied track, a driver acknowledgement shall be requested.

## Requirement 4.2.3.6a

REQ-2007-ERTMS-4.2.3.6a: The train shall be supervised according to train speed data available.

## Requirement 4.2.3.6b

REQ-2007-ERTMS-4.2.3.6b: The train shall, as a minimum, be supervised to a ceiling speed; the supervised speed shall not be shown on the DMI unless selected by the driver.

## Requirement 4.2.3.6c

REQ-2007-ERTMS-4.2.3.6c: The target distance shall not be shown on the DMI unless selected by the driver.

## Requirement 4.2.3.6d

REQ-2007-ERTMS-4.2.3.6d: On request of the RBC, the driver shall have the possibility to confirm that the track ahead of him until the end of the on sight section is clear

### 4.3 Trainborne Functions

#### 4.3.1

## Requirement 4.3.1.1

REQ-2007-ERTMS-4.3.1.1: ETCS shall collect all relevant information concerning train and line speed.

## Requirement 4.3.1.2a

REQ-2007-ERTMS-4.3.1.2a: ETCS shall calculate the permitted speed for the train for all locations of the authorised movement.

## Requirement 4.3.1.2b

REQ-2007-ERTMS-4.3.1.2b: This static train speed profile shall also respect maximum line speed and track speed and special speed levels for special classes of trains.

## Requirement 4.3.1.4a

REQ-2007-ERTMS-4.3.1.4a: The ETCS trainborne equipment calculates the static train speed profile on the basis of infrastructure data and train data.

#### 4.3.2 Dynamic train speed profile calculation

## Requirement 4.3.2.1a

REQ-2007-ERTMS-4.3.2.1a: Based on all relevant data, the ETCS shall calculate an emergency braking curve and a service braking curve

## Requirement 4.3.2.1b

REQ-2007-ERTMS-4.3.2.1b: Based on all relevant data, the ETCS shall calculate an emergency braking curve and a service braking curve

## Requirement 4.3.2.2a

REQ-2007-ERTMS-4.3.2.2a: When changing to a lower speed level, the front end of the train shall respect the dynamic train speed profile.

## Requirement 4.3.2.2b

REQ-2007-ERTMS-4.3.2.2b: When changing to a higher speed level the rear end of the train shall respect the static train speed profile.

## Requirement 4.3.2.3

REQ-2007-ERTMS-4.3.2.3: It shall be possible to define certain locations (e.g. tunnels) where speed increase is related to the front of the train.

## Requirement 4.3.2.5

REQ-2007-ERTMS-4.3.2.5: The braking curves shall ensure that the train complies with its speed requirements.

## Requirement 4.3.2.7

REQ-2007-ERTMS-4.3.2.7: Where failure to apply the full service brake is detected the emergency brake shall stop the train in rear of the danger point.

#### 4.3.3 Release speed calculation

## Requirement 4.3.3.1

REQ-2007-ERTMS-4.3.3.1: The release speed shall be calculated on board, based on either: safety distance and overlap accuracy of odometry deceleration performance of the train, etc or given from the trackside. The release speed given from the trackside shall take priority over the release speed calculated on board.

## Requirement 4.3.3.2c

REQ-2007-ERTMS-4.3.3.2c: The release speed shall be indicated on the DMI.

## Requirement 4.3.3.2d

REQ-2007-ERTMS-4.3.3.2d: If the release speed is calculated on board it shall ensure that the train will stop before reaching the danger point

## Requirement 4.3.3.3

REQ-2007-ERTMS-4.3.3.3: When the train is stationary or after a certain time (e.g. the time for "route releasing" of the overlap, the release speed calculation shall be based on the distance to the danger point (if calculated on-board). The condition for this change shall be defined for each target as infrastructure data.

## Requirement 4.3.3.4

REQ-2007-ERTMS-4.3.3.4: Each railway shall have the possibility of allowing a different release speed for every signal.

#### 4.3.4 Train location

## Requirement 4.3.4.1

REQ-2007-ERTMS-4.3.4.1: The ETCS trainborne equipment shall be able to determine the location of the entire train.

## Requirement 4.3.4.2

REQ-2007-ERTMS-4.3.4.2: On lines fitted with RBC, the ETCS trainborne equipment shall be able to transmit the location of the entire train to the RBC.

## Requirement 4.3.4.3

REQ-2007-ERTMS-4.3.4.3: The train location calculation shall take into account error of odometry.

#### 4.3.5 Speed calculation and indication

## Requirement 4.3.51a

REQ-2007-ERTMS-4.3.51a: Actual speed shall be indicated on the DMI

## Requirement 4.3.5.2

REQ-2007-ERTMS-4.3.5.2: There shall be no discrepancy between the speed shown to the driver and the speed used for supervision of movement authorities and speed limits, function 4.3.7

#### 4.3.6 Indication displayed on the DMI

## Requirement 4.3.6.3

REQ-2007-ERTMS-4.3.6.3: The indication provided shall enable the driver to drive at the permitted speed without receiving a warning and without intervention of ETCS.

## Requirement 4.3.6.4

REQ-2007-ERTMS-4.3.6.4: The driver shall know the distance to the next point defining the indicated braking curve and the permitted speed allowed. This shall be shown to the driver in a way that is understandable and logical.

## Requirement 4.3.6.5

REQ-2007-ERTMS-4.3.6.5: Visual and acoustic warnings to the driver about possible intervention from ETCS shall be given to enable the driver to react and avoid intervention.

## Requirement 4.3.6.6

REQ-2007-ERTMS-4.3.6.6: The driver shall have the possibility to select the language, this does not concern non pre-defined texts sent from the trackside.

##### 4.3.7 Supervision of movement authorities and speed limits

## Requirement 4.3.7.1

REQ-2007-ERTMS-4.3.7.1: A train shall be supervised to its static and dynamic train speed profiles.

## Requirement 4.3.7.2

REQ-2007-ERTMS-4.3.7.2: Within the braking curve area, a warning shall be given to the driver to enable him to react and avoid intervention from ETCS equipment at least 5 sec. before the intervention.

## Requirement 4.3.7.3

REQ-2007-ERTMS-4.3.7.3: If the train or the shunting movement exceeds the permitted ceiling speed by a certain harmonised margin, the trainborne equipment shall execute a brake intervention until the actual speed does not exceed permitted speed; then the driver shall be able to release the brake

## Requirement 4.3.7.4b

REQ-2007-ERTMS-4.3.7.4b: The driver shall be able to release an ETCS emergency brake application when stationary.

## Requirement 4.3.7.4c

REQ-2007-ERTMS-4.3.7.4c: If decided by a national value, the driver may release the ETCS emergency brake when the actual speed is below the permitted speed.

##### 4.3.9 Roll away and reverse movement protection

## Requirement 4.3.9.1a

REQ-2007-ERTMS-4.3.9.1a: To protect a traction unit from roll away and unwanted reverse movements the trainborne equipment shall monitor the direction of movement in relation to the permitted direction.

## Requirement 4.3.9.1b

REQ-2007-ERTMS-4.3.9.1b: The trainborne equipment shall apply the emergency brake after a distance, defined by a national value, is travelled by the train.

## Requirement 4.3.9.1c

REQ-2007-ERTMS-4.3.9.1c: The roll away/reverse movement intervention shall be indicated on the DMI.

## Requirement 4.3.9.2

REQ-2007-ERTMS-4.3.9.2: When the traction unit has come to a standstill, the driver shall be able to release the emergency brake.

## Requirement 4.3.9.3

REQ-2007-ERTMS-4.3.9.3: After releasing the emergency brake ETCS will provide the supervision appertaining when roll away protection was initiated

## Requirement 4.3.9.4

REQ-2007-ERTMS-4.3.9.4: When using more than one traction unit this function shall be disabled in all but the leading traction unit.

##### 4.3.10 Recording the ETCS information

## Requirement 4.3.10.2

REQ-2007-ERTMS-4.3.10.2: All data entered, received or indicated to the driver shall be recorded onboard. All data shall be related to UTC (Universal Time Corrected) and a reference point.

## Requirement 4.3.10.3

REQ-2007-ERTMS-4.3.10.3: Information shall be recorded to an accuracy which enables a clear view of the functioning of ETCS and way the traction unit has been driven.

## Requirement 4.3.10.4a

REQ-2007-ERTMS-4.3.10.4a: Standardised output interfaces shall enable transmission of information recorded to other media for investigation

## Requirement 4.3.10.5

REQ-2007-ERTMS-4.3.10.5: The retention period for the recorded data will be different and two levels are foreseen: Data to enable investigation of accidents need only be stored for at least 24 hours, and shall be very detailed. Operational data to enable assessment of driver performance shall be stored for at least one week.

## Requirement 4.3.10.7

REQ-2007-ERTMS-4.3.10.7: The following information shall be recorded: any transition of Level and of operational status the driver’s confirmation of transition to shunting train supervision data and information received from national train control systems actual speed full service brake intervention emergency brake intervention applying the train trip function selection of the override control override of the route suitability function isolation of on board ETCS equipmen data entered, recieved or indicated to the driver

### 4.4 Special Operations

#### 4.4.1 Using multiple traction units

## Requirement 4.4.1.1

REQ-2007-ERTMS-4.4.1.1: It shall be possible to use multiple traction units without isolating the ETCS trainborne equipment on traction unit(s) with an in-operative cab.

## Requirement 4.4.1.2

REQ-2007-ERTMS-4.4.1.2: Information received shall not influence the traction unit(s) with in-operative cabs.

## Requirement 4.4.1.3

REQ-2007-ERTMS-4.4.1.3: The train trip function 4.6.12 shall be suppressed in traction unit(s) with in-operative cabs.

#### 4.4.2 Using multiple traction units

## Requirement 4.4.2.1

REQ-2007-ERTMS-4.4.2.1: It shall be possible to use tandem traction units without isolating the ETCS trainborne equipment on the tandem traction unit.

## Requirement 4.4.2.2

REQ-2007-ERTMS-4.4.2.2: The train trip function 4.6.12 shall be suppressed on the tandem traction unit.

## Requirement 4.4.2.5

REQ-2007-ERTMS-4.4.2.5: The driver shall enter the driver ID

#### 4.4.7 Train reversing

## Requirement 4.4.7.1

REQ-2007-ERTMS-4.4.7.1: It shall be possible to drive the train backwards in a supervised way (speed and distance) according to information received from trackside

### 4.5 Functions required in the event of incidents or other (non ETCS) system failures

#### 4.5.2 Passing a stop signal with restricted movement authority

## Requirement 4.5.2.1

REQ-2007-ERTMS-4.5.2.1: The train speed shall be at or below a speed specified by a national value.

## Requirement 4.5.2.2a

REQ-2007-ERTMS-4.5.2.2a: The driver shall select an override control according to the permission received.

## Requirement 4.5.2.2b

REQ-2007-ERTMS-4.5.2.2b: The override control shall be protected against inadvertent operation.

## Requirement 4.5.2.3

REQ-2007-ERTMS-4.5.2.3: When the train passes the stop signal, the train trip function shall be suppressed.

## Requirement 4.5.2.4

REQ-2007-ERTMS-4.5.2.4: Actual speed shall still be shown on the DMI.

## Requirement 4.5.2.5a

REQ-2007-ERTMS-4.5.2.5a: A special indication shall be shown on the DMI.

## Requirement 4.5.2.5b

REQ-2007-ERTMS-4.5.2.5b: The supervised speed shall not be shown on the DMI.

## Requirement 4.5.2.7

REQ-2007-ERTMS-4.5.2.7: The train shall be capable of receiving any track-to-train information intended and relevant for this train including movement authority.

### 4.6 Protection Functions

#### 4.6.4 Emergency stop to train(s)

## Requirement 4.6.4.1a

REQ-2007-ERTMS-4.6.4.1a: If supervised by an RBC it shall be possible to command an emergency stop to all trains in a particular area or to a specific train

## Requirement 4.6.4.1b

REQ-2007-ERTMS-4.6.4.1b: It shall be possible to command an immediate train stop.

## Requirement 4.6.4.1c

REQ-2007-ERTMS-4.6.4.1c: It shall be possible to command a conditional emergency stop. If the train has already passed the location for the emergency stop the command shall be ignored

## Requirement 4.6.4.7

REQ-2007-ERTMS-4.6.4.7: When a train has received an emergency stop ETCS shall command the emergency brake.

## Requirement 4.6.4.8

REQ-2007-ERTMS-4.6.4.8: The emergency stop shall be indicated to the driver on the DMI.

#### 4.6.11 Route suitability

## Requirement 4.6.4.1a

REQ-2007-ERTMS-4.6.4.1a: It shall be possible to prevent a train from entering a route for which it does not meet the required criteria.

## Requirement 4.6.4.1c

REQ-2007-ERTMS-4.6.4.1c: Route unsuitability shall be indicated on the DMI.

## Requirement 4.6.4.2

REQ-2007-ERTMS-4.6.4.2: The driver shall be able to override the function when the train is stationary.

## Requirement 4.6.4.3

REQ-2007-ERTMS-4.6.4.3: After overriding this function the movement authority shall be re-established.

#### 4.6.12 Train trip

## Requirement 4.6.12.1

REQ-2007-ERTMS-4.6.12.1: When a traction unit passes a stop-signal the emergency brake shall be triggered.

## Requirement 4.6.12.2

REQ-2007-ERTMS-4.6.12.2: Operation of the train trip shall be indicated on the DMI.

## Requirement 4.6.12.3

REQ-2007-ERTMS-4.6.12.3: The emergency brake shall be applied until the traction unit is stationary.

## Requirement 4.6.12.4

REQ-2007-ERTMS-4.6.12.4: When the traction unit is stationary the driver shall be required to acknowledge the train trip condition. This acknowledgement will release the emergency brake.

## Requirement 4.6.12.5a

REQ-2007-ERTMS-4.6.12.5a: After the acknowledgement the driver shall be able to continue the movement

## Requirement 4.6.12.5b

REQ-2007-ERTMS-4.6.12.5b: After the acknowledgement the train shall be able to be driven backwards for a certain distance defined by national value

### 4.7 Train Control Centre Functions

#### 4.7.1 Train identification

## Requirement 4.7.1.1

REQ-2007-ERTMS-4.7.1.1: The ETCS trainborne equipment shall transmit its own train identification to the RBC.

## Requirement 4.7.1.4

REQ-2007-ERTMS-4.7.1.4: The train running number shall consist of a maximum of 8 numeric digits.

#### 4.7.3 Geographical position of the train

## Requirement 4.7.3.2

REQ-2007-ERTMS-4.7.3.2: On demand, the position of the front end of the train at the time of the demand shall be indicated on the DMI. This shall be possible while the train is moving or stationary.

### 4.8 Additional Functions

#### 4.8.1 Control of pantograph and power supply

## Requirement 4.8.1.1

REQ-2007-ERTMS-4.8.1.1: The ETCS on-board shall be capable of receiving information about pantograph and power supply from the trackside.

## Requirement 4.8.1.5a

REQ-2007-ERTMS-4.8.1.5a: The ETCS trainborne equipment shall indicate on the DMI the information regarding pantograph and power supply.

## Requirement 4.8.1.6

REQ-2007-ERTMS-4.8.1.6: The information regarding lowering and raising of the pantograph and opening/closing of the circuit breaker shall be provided separately and in combinations.

#### 4.8.2 Air tightness control

## Requirement 4.8.2.1

REQ-2007-ERTMS-4.8.2.1: The ETCS on-board shall be capable of receiving information regarding air tightness from the trackside.

#### 4.8.8 Plain text transmission

## Requirement 4.8.8.1

REQ-2007-ERTMS-4.8.8.1: It shall be possible to send plain text messages from track to train.

## Requirement 4.8.8.3

REQ-2007-ERTMS-4.8.8.3: When the plain text message appears on the DMI, the driver shall be alerted.

## Requirement 4.8.8.5

REQ-2007-ERTMS-4.8.8.5: The onboard equipment shall display plain text messages as received.

## Requirement 4.8.8.6

REQ-2007-ERTMS-4.8.8.6: The character set used shall support different languages.

#### 4.8.9 Fixed text messages

## Requirement 4.8.9.1

REQ-2007-ERTMS-4.8.9.1: It shall be possible to send fixed text messages from track to train

## Requirement 4.8.9.2

REQ-2007-ERTMS-4.8.9.2: Fixed text messages shall be provided in the language selected by the driver

#### 4.8.10 Management of special brakes

## Requirement 4.8.10.1

REQ-2007-ERTMS-4.8.10.1: It shall be possible to send information regarding the inhibition of the following different types of brake: Regenerative brake Eddy current brake Magnetic shoe brake

## Requirement 4.8.10.2

REQ-2007-ERTMS-4.8.10.2: Information shall be shown on the DMI

### 4.9 Functions primarily related to RBC

#### 4.9.5 Train Integrity

## Requirement 4.9.5.1

REQ-2007-ERTMS-4.9.5.1: The ETCS on-board shall be capable of sending to the trackside train integrity information detected by a system outside ETCS

## Requirement 4.9.5.4

REQ-2007-ERTMS-4.9.5.4: The driver shall be able to confirm the train integrity to the RBC manually. The confirmation requires the train to be stationary.

#### 4.9.9 Train Data to be sent to trackside

## Requirement 4.9.9.1

REQ-2007-ERTMS-4.9.9.1: The on board shall be capable of sending train data to the trackside after confirmation by the driver, or when entering the RBC area

## Requirement 4.9.9.2

REQ-2007-ERTMS-4.9.9.2: The following train data shall be sent from the on board to the trackside: Train running number STM ready for use train gauge Max. axle load status of air tight system type of el. power accepted international train category max. train speed train length

#### 4.9.10 Revocation of a Movement Authority

## Requirement 4.9.10.1

REQ-2007-ERTMS-4.9.10.1: It shall be possible to revoke a Movement Authority that has already been issued to a train in a co-operative way between RBC and train.

## Requirement 4.9.10.2

REQ-2007-ERTMS-4.9.10.2: The co-operative revocation of the MA shall be possible to a new target location, proposed from RBC.

## Requirement 4.9.10.3

REQ-2007-ERTMS-4.9.10.3: The new target location shall be checked for acceptance by the on board.

## Requirement 4.9.10.4

REQ-2007-ERTMS-4.9.10.4: If a train cannot stop at the proposed new target location it shall reject the request and keep the old target location.

#### 4.9.11 Reversing

## Requirement 4.9.10.1

REQ-2007-ERTMS-4.9.10.1: The Reversing function shall only be possible in one active cab which is not closed at any time during the procedure.

## Requirement 4.9.10.2

REQ-2007-ERTMS-4.9.10.2: Reversing shall be possible as defined by a value given with the MA

## Requirement 4.9.10.5

REQ-2007-ERTMS-4.9.10.5: The driver shall be able to use the Reversing function without needing to re-confirm the train data.

## Requirement 4.9.10.6

REQ-2007-ERTMS-4.9.10.6: Reversing shall be supervised to a distance and speed set as National Values

## Requirement 4.9.10.7

REQ-2007-ERTMS-4.9.10.7: The distance supervised can be extended from the trackside.

## Requirement 4.9.10.8

REQ-2007-ERTMS-4.9.10.8: Once the train starts reversing the MA shall be cancelled.

#### 4.9.12 Handover when passing from one RBC area to another

## Requirement 4.9.12.1

REQ-2007-ERTMS-4.9.12.1: The train shall be able to automatically pass from one RBC area to another without driver intervention.

## Requirement 4.9.12.2

REQ-2007-ERTMS-4.9.12.2: If the train is equipped with two operational radios there shall be no performance penalty as a result of a transition from one RBC to another (train spacing and train speed).

## Requirement 4.9.12.3

REQ-2007-ERTMS-4.9.12.3: If the train is equipped with only one operational radio, passing from one RBC to another shall still be possible but might result in a performance penalty.

## 5 Failures and Fall-back Procedures

### 5.1 Interruption in transmission

#### 5.1.3 Transmission Failures

## Requirement 5.1.3.1

REQ-2007-ERTMS-5.1.3.1: In the event of a Transmission Failure the following reactions, shall be capable of being applied in accordance with a National Value: Option 1. The ETCS trainborne equipment shall immediately command the emergency brake. The failure shall be shown on the DMI. Option 2. The ETCS trainborne equipment shall immediately command the full service brake. The failure shall be shown on the DMI. Option 3. The train may proceed unrestricted to the end of its movement authority. The indication on the DMI shall remain, and the driver shall be informed about the loss of transmission.

### 5.2 On board equipment failures

#### 5.2.1

## Requirement 5.2.1.1

REQ-2007-ERTMS-5.2.1.1: If there are failures of the trainborne equipment which compromise the safety of train supervision, the ETCS trainborne equipment shall immediately command the brake and bring the train to a stop.

## Requirement 5.2.1.2a

REQ-2007-ERTMS-5.2.1.2a: The occurrence of a failure shall be displayed on the DMI.

## Requirement 5.2.1.2c

REQ-2007-ERTMS-5.2.1.2c: In ETCS with RBC this restriction on performance shall, if possible be transmitted to the RBC.

### 5.3 Fault indications to the driver

## 6 Driver-Machine Interface

## 7 Training

## 8 Reliability, Availability, Maintenability, Safety (RAMS)

## 9 Environmental Specification

## 10 Glossary

Describes terms used in the document. The title of a function is normally not described. Please refer to the note below for each function-title.

## 11 Other technical functions
