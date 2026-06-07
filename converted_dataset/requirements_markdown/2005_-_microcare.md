# Software Requirements Specification For Voucher Management System

- Source file: `2005 - microcare.xml`
- Version: 1.0

## 1 Introduction

### 1.1 General overview of the VMUS (Voucher Maintenance Unit System)

System Development: The system will be developed on Oracle 9i platform Front end will be VB (visual basic) Reports will be crystal reports 9 System design: The system will be user friendly with maximum master table structure with all transaction screens to have drop down selection menus to minimize data entry errors. The main data entry screen on claims entry to have drop drown menu from patient’s profile selection to medicine cost to have drop down. Minimize the use of key board for any number entry to have a faster transaction data entry. The system will be easily trainable for the user with minimum computer skill with simple user step by step manual. Storage efficiency: The structural design of the database will have sequential links with surrogate keys. The database storage will be highly efficient to manage and avoid empty unused spaced blocked, properly defragmenter on a periodic basis. This efficiency will have a maximum provision to expand this program beyond the pilot period, if the program requirements remain same. Security: High intrusion controls will be in place in the system and the database. Access level controls, various organizational level user setting by including granular model setting. External Hardware interface: Bar-code – the system will interface with the bar-code reader to interface all transaction details. E.g. voucher number verifications, claim form entry and selection of voucher usage by the clients. Bio-metrics – the system will interface with the thumb-print reader for verifying claims form used by the clients.

#### Diagram Functional Flow Diagram:

### 1.2 Purpose

The purpose of this document is to explain the flow and the requirement of Voucher Management System (VMU) required by Marie Stopes International Uganda (MSIU) during the various meetings held between MSIU and Microcare from 28th of Nov 2005 to 30th of Nov 2005. This document is purely based on the Functional Flow Diagram designed by Microcare. The document will explain every small entity of the system including various code generations, Bar-coding and Graphical User Interface etc. This document will help the system development team to understand the overall and detailed functions of every small entity in VMU and to design the system that will meet every requirement of the VMU program. This document will help the testing team to prepare the Test Cases and will help them to test every module in the system and overall testing of the system, so that the testing team will have confidence on the quality of this system.

### 1.3 Project Scope

#### 1.3.1 about MSIU and OBA Program

##### The concept of Output-based Aid (OBA)

Past experiences with development aid showed, that financing inputs, e.g. facilities and equipment, does not result in the necessary improvement of health outcomes. Thus as a change of paradigm, the OBA concept finances agreed outputs with predefined quality rather than pre-defined inputs by selling vouchers for STD services at subsidised prices to patients. These vouchers will be refunded to service providers in the private sector (medical doctors, qualified nurses and midwives), government hospitals, NGOs, and faith-based organisations. The major advantages of the OBA approach are, that it allows To target resources to address selected health problems, To target the provision of services to specific parts of the population and To stimulate private market initiative and competition.

##### Objective of the OBA Programme in Uganda is to provide

Quality health care services for STD treatment, For the sexually active population of the Mbarara district, Through a voucher system, By qualified, approved providers, For a pilot phase of 1 year.

##### Basic structures and processes of the STD voucher programme

The main structures and processes in the STD voucher programme are: The programme is prepared, implemented and managed by the Voucher Management Unit (VMU). The VMU establishes a network of approved providers (during the pilot phase private, NGO, FBO providers) throughout Mbarara District. The VMU runs a marketing and behavioural change campaign (BCC) to market and inform about the voucher services and how to use them. The VMU establishes and runs a distribution system with the purpose to distribute the STD vouchers to the sexually active population for which the above-mentioned providers are in reach.

#### 1.3.2 About Voucher Management system

The voucher management system VMS is designed to atomize the process of Voucher Management Unit (VMU) to minimize the manual process to maximize the quality of the project to understand the progress and timely out come of the project to take necessary steps by the MSIU Admin team to plan for the future and to increase the quality of the STD voucher service. The system will also control the existence of fraud in claims and will help the service provider to reach their payments in time without delay. The other features and details of system will be explained in below sections in the document. The voucher management system is subdivided into following modules to make the system easy for understanding, developing, testing and to implement. Voucher Creation / Preparation Marketing / Sales Claim Entry / Processing Voucher Sales Return Client Feed back Reports (Standard and Customized) Security and User Privileges

### 1.4 References

The preparation of SRS is purely based on the following documents Final report on Programme Design Study, Dated 10-Sepetember-2005 Prepared by MSIU Functional Flow of VMUS Prepared by Microcare on 30th November 2005.

## 2 Overall Description

### 2.1 System Perspective

This section of the document is going to explain the functionalities of the system, its subsystems and how it’s integrated and working together. During the system study, it was understood that the first pilot period, twenty thousand vouchers will be sold, but the VMU-system has the provision to upgrade to meet the additional market and projects needs.

#### 2.1.1 Outline of entire system

The VMU will create the vouchers and sell it to clients through distributors The distributor will submit the sales details back to the VMU. Each voucher should have two portions with three tear off voucher slips each for Client and Partner. The client and/or the partner will choose the service provider and will get treatment First visit is called as Consultation and if the patient is not cured then they can go for first follow up and second follow up, If the patient is not cured then the doctor will refer the patient to some other Hospitals the hospital may be another VSP or any other. Each visit details (including Diagnosis, Lab Test and Drugs) of the patient is called a claim, The VSP will submit the claim to VMIU field office to enter those into the database, The filed office will validate the claim form manually and through system, If any of mandatory information is missed or any false information is existing then the field office will reject the claim back to VSP and the system will keep those claim in a quarantine area The quarantined forms will be sent back to the VSP for verification, if the VSP returns the claim with satisfactory details, the claims will be entered on to the system, in the following month’s batch. Based on the payment terms agreed by VSP, the field office will generate BiMonth or Monthly financial and medical report and send it to MSIU Admin team to arrange the payments for the VSP. To understand the satisfaction of client the MSIU Admin team will get client feedback from some of the clients and send those documents to field office to enter those into database.

#### 2.1.2 2.1.2 Voucher Management System Modules

##### 1. Voucher Creation / Preparation

Voucher creation – the voucher numbers are system generated and created with unique identification numbers with security protocols in-built. The created unique numbers are then printed out in the form of bar-codes, which will complement (or stuck on the voucher) the voucher. Then at every level on the voucher cycle this number is captured, on distribution, retail sales, point of treatment, enclosed along with claim forms, at the claims processing and finally for the payment. Such tracking records will be utilized for reports as well. Each voucher should have the following properties, which will have sub-elements to get the batch numbers, voucher numbers, and the project codes. Project code – Group batch code – Batch number – Voucher number – Security code. Project Code (2 Digit) Example: P001 Group Batch (3 Digit) each group batch has a batch of 100 Batches Example: GP0001 Batch number (2 Digit) approximately each batch will have 10 vouchers Voucher number (10 digit) Security Code All codes will be printed out in the form of Bar Additionally the provision for validity date check for the period of vouchers to be used in the program is provided. This validity date can be amended or altered at the system level ONLY by the authorized user Voucher will also have MRP (maximum retail price) Voucher should have three tear off portioned slips with a sub-section tear-off for the partner. If the tear off voucher slips would be sticker then it will not be lost on attaching to the claim forms by the VSP. Each voucher slip should contain the bar code of the Voucher with two identifications one for the client and the other for the partner. The first tear for the first consultation Second one for the first follow-up And the third tear off for the final (second follow-up).

###### Design Constraints

This system has high security feature as far as the user access to the system, including all the modules, sub-modules and even at the screen level. The voucher will be created ONLY by the authorized person. The will be a provision to create a minimum quantity of vouchers at one time (such minimum numbers will be decided by the management team). Once created vouchers will not be edited or deleted but there will be a provision to with-hold any voucher number if the admin team decides to do for any reason. There will be a provision to amend the validity date of the voucher.

##### 2. Marketing / Sales

The marketing and sales is the next step and the next module in the system. This module will take care of following sub modules.

###### i Distributor Master Information

The system will capture the master details of every distributor so that the users can get the details of any distributor and sales details at any time. Each distributor will have unique code and detailed descriptions such as name, address, locations and type of business etc. such valid information will help us track information related to sales and distributions. Following fields will be captured at this master. Distributor Code (3 Digit) Example: DS0001* Name of the distributor* Type of business (e.g. hospital/pharmacy/NGO)* Proprietor Name* Designation Address (Street/Road, Sub District, County, Sub County and Village or Town)* Contact No Email Id Status (active/deactivate)

###### Design Constraints

The address field will capture the geographical location of the distributor, such as District, Sub-District, County, Sub-County or Village / Town, road or street. All the level of details will have a master table in order to update as per the program requirements. The system will check the duplicated ID for the distributors. The system can allow the duplicate names of the Distributor. On capture of any duplicate name the system will give a warning message to have the duplicate name or to change the name. For better reporting purposes it is better to have a differentiating indicator on the name. System will have a provision to print the distributor master details. The distributor screen will have a provision to view the Sales History of a particular distributor with following summary details. Distributor Name as Report Header and following as the report footer Batch No Date of purchase Qty Purchase Qty Sold Qty Returned Balance Qty (any other details required by the MSIU office)

###### ii

The system will capture the details of MSIU Salesman; this would help the MSIU management team to understand the performance of each Team or salesman. During every distribution transaction the user should select the name of the sales man listed from Team Master. The Salesman master should capture following information’s. Salesman Code* Name of the Salesman* DOB & Age* Gender* Communication Address* Contact No E-Mail Id Sales-team (which will have a separate master)*.

###### Design Constraints

The system will check the duplicated ID for the salesman and team. The system can allow the duplicate names of the salesman. On capture of any duplicate name the system will give a warning message to have the duplicate name or to change the name. For better reporting purposes it is better to have a differentiating indicator on the name

###### iii Distribution Transactions (Sales from MSIU to Distributor)

The system will capture the details of voucher sales between MISU sales team and Distributors. During the distribution the system will capture the following details, to make Distribution process easily. With the below details the user can get the details of Distributor-wise and Salesman-wise and Batch No wise sales details as reports. Name of the distributor* Name of the Sales Man* Date of distribution* No of vouchers sold* According to the number of vouchers required by the distributor, the system should allocate the relevant vouchers with their numbers and batch numbers based on the stock. Invoice amount = No of vouchers x Wholesale price Mode of payment is Cash

###### Design Constraints

The mandatory information required during a distribution transaction is mentioned below. Name of the distributor (Selecting from Distributor Master) Name of the Sales Man (Selecting from Sales man master) Date of Distribution (Date selection option) Required Qty (No of vouchers sold (Allow only Numeric Entry)) Invoice Amount = Whole Sale Rate (should taken from settings master based on sale date) * Qty Sold. (Automatic Calculation)

#### 3. Claim Entry/Processing

The program will take maximum care in this form and table, as it become a vital transaction to be captured. In this module you will see that every capture of data will be validated and checked on saving into the database. For e.g. the capture of voucher number, clinical information, diagnosis details, drug and investigation details and the costs are going to provide the program a vital report information. The system development team will focus its attention in making this module/table function efficiently. For the easy understanding and designing of the system, this module is subdivided into following sub-modules. The division of sub-module is purely based on the sub-level categories of the data information. The service (treatment) will happen at the VSP (Service Provider) clinic or hospital The attending doctor will fill the claims form. On completion of the service the patient will provide the voucher according to the visit type and patient type (client or partner), the voucher will be stuck to the claim form. The thumb print will also be placed on completion of the service The VSP will send the collected claim forms monthly and send it to MSIU field office. MSIU office will then process the claim.

##### i Voucher Service Provider (VSP) Master Information

The VSP master will have the following information: VSP Code Providers Name Physical Address (Street / Road, District, Sub-District, County, SubCounty, Village/Town) Communication Address (Street / Road, District, Sub-District, County, Sub-County, Village/Town) Health Sub-District Locality Level Of Facility Type of facility Registration Body Contact Person Designation Contact No E-Mail id Status (Active / In-Active)

###### Design Constraints

Other than Contact No and E-Mail Id all other information are mandatory during the creation of a new Service Provider. The VSP code is a digit code with suffix SP, would be automatically generated by the system. The system should generate message with two option “Continue – Yes/No” while the user trying to create a new VSP with an existing name, If the user press Yes the system will allow the user to enter the same, if not the system wont allow the new entry to save. The system will list District, Sub-District, County, Sub-County, Village / Town from the master during VSP creation, if any of them are not available in the system, then the system will have the provision to navigate quickly to its master screen and do enter master details and back to VSP screen. The values of Health Sub – District, Locality, Level Of Facility, Type of facility, Registration Body would be list from their own master and should select the details based on the VSP. If any of the information is not available in existing master of above, then the system will have the provision to navigate quickly to its form to enter the master details and back to VSP Screen. The system will populate Active VSP only on other screen during data entry process, but the system will also populate all VSP for report purpose. Activation and In-activation of VSP is purely based on the MSIU Management decision. But if the system is found more than two fraud entries during the claim process of particular VSP, then the system would automatically change the status of that particular VSP as In-activate. Activation of that particular VSP is again purely based on MSIU Management decision. The VSP Master Information screen should have a provision to enter the payment terms agreed between MSIU and VSP. The system will capture following master details to fill the payment terms. Payment Mode (Cash / Bank) Bank Account No Bank Name Payment Type (Selection from list of options Bi-Monthly/Monthly)

##### ii VSP Staff Master Information

The system will have the facility to capture the details of VSP staff details and the necessary master information while entering the claim into the system. VSP Name Staff Code Staff Name Staff Type Qualification

###### Design Contraints

The system will generate message while creating a new staff with existing name, but the system will allow the user to save that new staff if its required. All above information’s other than Qualification are mandatory during the creation of new staff under any VSP. The system will automatically create Staff Code with Suffix as VSP Code + SC + 3 digit. For example HP0001SC0001 Staff type (should be select from list of staff type listing from Staff Type Master) If any of the staff type is not available in the system, then the system should have the provision to navigate quickly to staff type master to enter the new staff type and then back to Staff Master screen.

##### iii Claim (Treatment Form) Submission

Depends on the payment terms (Bi-monthly / Monthly) mentioned in the VSP master the VSP should submit the Claim (Treatment form) to the MISU Field office. While submitting the Claim (Treatment Form) to MSIU, the system will have the provision to capture the following details. These information is vital and shall be used for compared with the processed claims. VSP Name Date of submission No of Mentioned Forms No of Available Forms The above as the master part and below details are the Transaction part Treatment Form No

###### Design Constraints

During submission entry all above information’s are mandatory Date of submission should be current date The system lists the VSP Name from VSP Master. Mentioned Forms and Available Forms only accept numeric values. Available forms may be less than or greater than or equal to Mentioned Forms. In the transaction part no of forms should match with No of Available Forms

##### iv

The claim entry is purely based on the Treatment (claims) Form submitted by the VSP. Before the claim entry the user should check the form manually to understand whether any mandatory information is missed in the Claim or not. If yes, then the user should mark that Claim (Treatment Form) status as Rejected and send back to VSP. During the claim entry the system should capture the following information. Treatment Form No Claim No Submitted Date VSP Name Voucher No Visit Count Patient Type Patient Name Age Gender Address (Street / Road, District, Sub-District, County, Sub-County, Village / Town) Contact No Doctor Name Doctors Note HIV Details if any Patient Status Claim Amount Claim Status

###### For Fist time Consultation

Syndrome Clinical Examination Diagnosis Lab Test Drugs Name – Frequency –No of days - Qty Other measure

###### For First Follow UP

Diagnosis Drugs Name – Frequency –No of days - Qty

###### For Second Follow UP

Diagnosis Drugs Name – Frequency –No of days - Qty

###### Design Constraints

All above master level information are mandatory other than Contact No during the entry of claim into the system. The following part will explain how the systems will validate every information during claim entry. Treatment Form No (List Form No from Claim receipt details which all are not yet entered in claim) Claim No (The system will automatically generate the Claim number with Hospital Code as Suffix + 8 digit) Submitted Date (This should populate automatically while choosing the Form No) VSP Name (This should populate automatically while choosing the Form No) Voucher No (This should be captured from Bar Code reader based on the Voucher Slip Stick on the Claim Form) Visit Count (This should be captured from Bar Code reader based on the Voucher Slip Stick on the Claim Form) Patient Type (This should be captured from Bar Code reader based on the Voucher Slip Stick on the Claim Form) Patient Name Age Gender (Select from the list of options Male / Female) Address (Street / Road, District, Sub-District, County, Sub-County, Village / Town) other than Street / Road all other details would list from the its master records, if any details are not exist in Master record, then the system should have the provision to navigate quickly to its master screen to enter the new details and back to the Claim Entry Screen Contact No Not Mandatory Doctor Name (select from list of doctors populating from VSP Staff Master) Doctors Note – Space for the doctor to enter the note about the patient if anything is required HIV Details if any – The format for HIV capturing details are attached with SRS. Patient Status - (Select from list of status options populating from Patient Status Master) suppose the status is Referral then the system will have the provision to capture Referred To and Reason for Referral, the reason for Referral should be populated from Referral master. Claim Status – Status of the claim is depends information available in the Claim, if any false data or any mandatory information is available in Claim, then the claims status will change, if the value of status is not “Accepted” then the claim will be stored in quarantine area and can able to precede it further from its status. The system should have a provision to capture the reason suppose if the claim status is “Rejection or Quarantine” Claim Amount – The calculation of claim amount is explained below.

###### Details about Masters information  required for Claim Processing

Generic Master with following information Code Name Drugs Master (there will (can) be a standard drug price for all VSP provision) Generic Name Drug Code Drug Name Retail Price Syndrome Master Syndrome Code Syndrome Description Clinical Examination Master Exam Code Exam Description Diagnosis Master Diagnosis Code Diagnosis Description Lab Test Master Test Code Test Name Other Measure Master Measure Code Measure Description Patient Status Master Status Code Status Description Claim Status Master Status Code Status Description Referral Reason Master Reason Code Reason Description Claim Quarantine / Rejection Reason Master Reason Code Reason Description MSIU Treatment Matrix Syndrome First Visit Clinical Examinations First Visit Diagnosis Lab Test First Visit Drugs First Visit other measures Syndrome First follow up Diagnosis First follow up Drugs Syndrome Second follow up Diagnosis Second follow up Drugs

###### Assumptions

The VSP should follow MSI Patter for treatment The user should enter the information exactly into the system from the manual claim form The VSP staff should get the thump impression from the patient and should stick the voucher slip on the claim form System only accept claims only if the mandatory information is complete System should calculate Claim Amount only based on treatment matrix

#### 4. Voucher Sales Return

Voucher Sales return is feature used when a distributor is planning to return the vouchers back to the MSIU sales team. The system will capture the following information during the sales return transaction. Distributor Name Sales Man Name Sales Return Date Sales Return Amount (No of voucher returned x whole sale rate) Number of vouchers Returned

##### Design Constraints

All above information are mandatory during the sales return Distributor Name - will list from Distributor Master Sales Man Name - will list from Sales Man Master Sales Return Date – System date is default and it should be less than or equal to system date

#### 5.

MSIU team collects the client feed back from the clients who got treatment through the voucher system. The Client Feed back form should capture the following details Voucher No Client Details Details of syndromes treated Lab Test Drugs Details Success of Treatment Referral To Treatment Satisfaction of Treatment (Not at all / Moderate / Good / Completely) Satisfaction of counseling - Enter by the user Satisfaction of ensuring privacy – Enter by the user Partner Treated

##### Design Constraints

Based on the Voucher No the system will populate the following details Client Details (Address as per Claim Form will populate automatically) Details of syndromes treated (Automatically populate from the system based on Voucher No) Lab Test Details (Automatically populate from the system based on Voucher No) Drugs Details (Automatically populate from the system based on Voucher No) Success of Treatment (Automatically populate from the system based on Voucher No) Referral To Treatment (Automatically populate from the system based on Voucher No) Partner Treated (Treatment (Automatically populate from the system based on Voucher No)

##### Assumptions

The user should enter correct Voucher No The user will not alter any information about treatment, which is populating from the system

#### 6. Reports (Standard and Customized)

As per the MSIU Project Document named “Programme Design Study” the following reports are required Monthly after claim collection on clean claims to be paid without reservation Monthly after claim collection on claims, where payment shall be withheld until clarification Report on claims per provider Report, summarising all providers Quarterly summary reports per provider and summarising all providers Frequencies of syndromes treated, additional information on patient population (sex, age) Frequencies of primary clients and notified partners Number of correctly documented cases, cases with incorrect documentation, cases treated according to algorithms, cases with justified treatment alterations and treatment errors Summary report comparing the different providers regarding syndromes treated, documentation quality and treatment behaviour Quarterly and half yearly reports giving the time trends of the abovementioned indicators for each provider and all providers combined

#### 7. Security and User Privileges

The security setting of the entire system is based on User Group. The roles available in the system are allocated to user group. The user group creation would capture the following Information Group Code Group Name

##### Design Constraints

Allow above information are mandatory while creating a new User Group. The system admin only can able to create User Groups The system should have the provision to create any number of individual user under any user group. Each Individual User should have the following information Group Name (Selecting from User Group) User Name Password Verify Password
