# Software Requirements Specification (SRS) Gamma-J Connecting Retailers through the World Gamma-J Gamma-J Web Store

- Source file: `0000 - gamma j.xml`
- Version: 0.0

## 1 Introduction

### 1.1 Purpose

This is the Software Requirements Specification for GAMMA-J’s Web Store. This Web Store is designed to allow new online store owners a quick and easy means to setup and perform sales and other core business over the internet. This document will outline all of the functions, capabilities and requirements for Version 1 of GAMMA-J’s Web Store. Version 1 is planned for implementation on a “plug and play” USB Key. Future versions will be based on other network appliances.

### 1.2 Document Conventions

None

### 1.3 Intended Audience, Reading Suggestions

This document is intended to flush out the requirements by the customer GAMMA-J. The customer can review this document to ensure their needs along with the needs of their user’s are being met in their new Web Store program. The development team will also use this document for guidance on overall design and implementation of the Web Store system. The test and verification team can reference this to ensure the requirements are being meet for the customer. Finally, the tech writer will use this to assist with user documentation. This document is designed to be review from beginning to end; however, readers who are new to technical documentation may want to refer to Appendix E: Data Dictionary first.

### 1.4 Project Scope

According to GAMMA-J’s Functional Needs Statement this Web Store will: Manage customer accounts Manage an online store inventory Confirm Orders Have an unambiguous interface to assist in browsing the categories and products Use Secure Socket Layer (SSL) for security Have an availability of 99.999% Allow an optional mirror site for reliability and backups Feature interface for future software enhancement via “Plug-ins” The initial inventory will be 100 items. Expandable with unique codes, the owners can purchase to expand the inventory. The minimum total inventory will be 20,000 items. Since this will be a “Plug and Play device”, no software installation will be necessary. This software will contain all of the basic needs to manage an online store. Advanced needs can be added in the future via “plug-ins.” More detail on the functionality of the Web Store can be found in part 3. System Features and in the function Needs statement.

### 1.5 References

This document draws insight from the Web Store System Overview, Functional Needs Statement, and Stakeholder Goals List.

## 2 Overall Description

### 2.1 Product Perspective

Web Store is a new system designed for users new to the online E-commerce. This will be a plug and play device with its own CPU and operating system. The Web Store will be a quick and easy means to setup and operate an online Web Store. The Figure 2.1 is a context diagram showing external system interfaces.

### 2.2 Product Features

Account Management (AM) (High Priority): AM allows users to create, edit, and view accounts information. It also allows the user to login/out of the system. Search Engine (SE) (Medium Priority): SE is the tool that assists the user in finding a specific item in the database. It can receive search criteria, find search criteria, and return the results of the search. Product Management (PM) (High Priority): PM allows sales personnel to manage the product line shown on the web site. Shopping Cart (SC) (Medium Priority): SC is temporary storage for customers shopping on the web. Items from the inventory can be reserved in a virtual cart until the customer decides to purchase them. Purchasing and Payment (PP) (High Priority): PP is used to approve and transfer payment from buyers when purchasing items in the cart.

### 2.3 User Classes

System Administrator: Is generally the owner that takes care of maintenance for the Web Store system. The administrator will be in charge of assigning privileges of accounts. Suggested more than one individual can have administrator privilege to ensure advisability. Full documentation will be provided to the Administrator to assist with this process. Sales Personnel: Is generally the owner of the Web Store tasked with updating inventory and product line descriptions. Once added, sales personnel can add, delete and change descriptions, pictures, prices, and when ready flag items for customers to buy. Customer: A customer is an individual wishing to purchase inventory from GAMMA-J’s Web Store. The Web store will have a variety of clientele depending upon the inventory loaded on the Key. When creating a new account on Web Store it will default as a customer account. Later if the account needs to be upgraded the administrator can accomplish this via the administrator interface.

### 2.4 Operating Environment

## Requirement OE-1

REQ-0000_-_GAMMA_J-OE-1: Web Store shall operate with the following internet browsers: Microsoft Internet Explorer version 6 and 7, Netscape Communicator Version 4 and 5.

## Requirement OE-2

REQ-0000_-_GAMMA_J-OE-2: Web Store shall operate on an Intel based system with Slackware Linux 2.6 and Apache Web Server. The operating system is designed by the Yoggie Corporation. Although maintenance documentation will be supplied and the operating system will be tested, the developers of this Web Store are not responsible for the functionality of the operating system.

## Requirement OE-3

REQ-0000_-_GAMMA_J-OE-3: The system shall use SQL based database to store inventory information.

## Requirement OE-4

REQ-0000_-_GAMMA_J-OE-4: USB interface and divers are provided by Yoggie Corporation.

### 2.5 Design and Implementation Constraints

## Requirement CO-1

REQ-0000_-_GAMMA_J-CO-1: Must use a SQL based database. SQL standard is the most widely used database format. Restricting to SQL allows easy of use and compatibility for Web Store.

## Requirement CO-2

REQ-0000_-_GAMMA_J-CO-2: Compatibility is only tested and verified for Microsoft Internet Explorer version 6 and 7, Netscape Communicator Version 4 and 5. Other versions may not be 100% compatible. Also other browsers such as Mozilla or Firefox may not be 100% compatible.

### 2.6 User Documentation

## Requirement UD-1

REQ-0000_-_GAMMA_J-UD-1: Shall install online help for users via the web interface

## Requirement UD-2

REQ-0000_-_GAMMA_J-UD-2: Shall deliver Operations and Maintenance manual, Users Guide book, and Installation Instructions for the Administrator.

### 2.7 Assumptions and Dependencies

## Requirement AD-1

REQ-0000_-_GAMMA_J-AD-1: Assume the delivery of development, test and evaluate samples of the USB system from Yoggie.

## Requirement AD-2

REQ-0000_-_GAMMA_J-AD-2: Assume Yoggie will freeze the baseline of the USB system after delivery.

## 3 System Features

### 3.1 Customer Accounts

#### 3.1.1 Description And Priority

Customers will be able to create accounts to store their profiles, contact information, purchase history, and confirm orders. This is a high priority system feature. Security methods will ensure that customer accounts remain confidential and resistant to tampering.

#### 3.1.2 Stimulus/Response Sequences

Web Browser initiates request to Web Server via HTTPS Web Server parses request Web Server submits request to Service Service picks up request Service runs task Service returns results Web Server checks for completion Web Server returns results to Web Browser Web Browser displays results

#### 3.1.3 Functional Requirements

Customers will be able to create accounts to store their customer profiles, configure contact information, view their purchase history, and confirm orders. Customers will be able to register, log in, and log out of their accounts. Furthermore, Customer profiles will also include payment information, such as the ability to store credit card information, and address information.

### 3.2 Inventory Management

#### 3.2.1 Description And Priority

Inventory management will allow for the placement of products into multi-tiered categories. This is a medium priority system feature.

#### 3.2.2 Stimulus/Response Sequences

Same as 3.1.2

#### 3.2.3 Functional Requirements

Products will be stored in multi-tiered categories; a category can contain sub categories or products. The inventory management will allow for administrators to update the categories, the products placed in categories, and the specific product details.

### 3.3 Shopping Cart

#### 3.3.1 Description And Priority

Customers will be able to add and store products for purchase within the shopping cart. This feature is a medium priority system feature.

#### 3.3.2 Stimulus/Response Sequences

Same as 3.1.2

#### 3.3.3 Functional Requirements

Customers will also be able to add products into the shopping cart. The shopping cart will clearly display the number of items in the cart, along with the total cost. The customer will also be able to add to or remove products from the shopping cart prior to checkout and order confirmation.

### 3.4 Order Confirmation

#### 3.4.1 Description And Priority

Order confirmation will allow the customer to review their order after checkout prior to confirmation. This is a medium priority system feature.

#### 3.4.2 Stimulus/Response Sequences

Same as 3.1.2

#### 3.4.3 Functional Requirements

Customers will be able to confirm the order after checkout. If the order is incorrect, the customer will be able to revise and update their order. The customer will then receive a confirmation email with the specific order details.

### 3.5 Interface

#### 3.5.1 Description And Priority

The interface will be presented to the customer in a web browser. The interface must remain consistent among various web browsers and be intuitive to the customer. This is a medium priority system feature.

#### 3.5.2 Stimulus/Response Sequences

Same as 3.1.2

#### 3.5.3 Functional Requirements

Customers will be presented with an unambiguous interface to assist in browsing the categories and products. Customers will be able to search for products matching their search criteria. The interface will be compatible with all major web browsers such as Internet Explorer, Mozilla Navigator, Mozilla Firefox, Opera, and Safari.

### 3.6 Interface

#### 3.6.1 Description And Priority

The system will feature an API to allow customers to build custom plug-ins to be able to meet their needs. This is a high priority system feature as it ensures the flexibility of the system to be tailored to specific needs.

#### 3.6.2 Stimulus/Response Sequences

Web Browser initiates request to Web Server via HTTPS Web Server parses request Web Server submits request to API Service API Service picks up request API Service submits request to Plug-in Plug-in picks up request Plug-in runs tasks Plug-in returns results API Service validates results API Service returns results Web Server checks for completion Web Server returns results to Web Browser Web Browser displays results

#### 3.6.3 Functional Requirements

The system will implement an Application Interface to allow for various plug-ins to interact with the system. The plug-in API will be well documented and specifications will be provided to plug-in developers.

## 4 External Interface Requirements

### 4.1 User Interfaces

FIGURES

### 4.2 Hardware Interfaces

HI-1: USB key from Yoggie

### 4.3 Software Interfaces

#### SI-1: WebOrder Browser Interface

SI-1.1: The order database of WebOrder will communicate with the account system through a programmatic interface for the billing operations. SI-1.2: Through programmatic interface, WebOrder will transmit information of items ordered by customers to the Inventory management system. SI-1.3: Plug-ins interface

### 4.4 Communications Interfaces

CI-1: The WebOrder system shall send an e-mail confirmation to the customer that the items they ordered will be delivered to the shipping address along with tracking number. CI-2: The WebOrder system shall send an e-mail to System Administrator regarding any technical queries from customers or sales people.

## 5 Quality Attribute Requirements

### 5.1

## Requirement 1

REQ-0000_-_GAMMA_J-1: Upon the USB being plugged in the system shall be able to be deployed and operational in less than 1 minute.

## Requirement 2

REQ-0000_-_GAMMA_J-2: The system shall be able to handle 1000 customers logged in concurrently at the same time.

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system shall be able to retrieve 200 products per second.

## Requirement 4

REQ-0000_-_GAMMA_J-4: The system shall be able to add product to shopping cart in less than 2ms.

## Requirement 5

REQ-0000_-_GAMMA_J-5: The system shall be able to search for a specified product in less than 1 second.

## Requirement 6

REQ-0000_-_GAMMA_J-6: The system shall be able to email customer and vendor in less than 1 second.

## Requirement 7

REQ-0000_-_GAMMA_J-7: The system shall be able to validate credit card in less than 2 seconds.

## Requirement 8

REQ-0000_-_GAMMA_J-8: The system shall be able to acquire shipping charges in less than 2 seconds.

## Requirement 9

REQ-0000_-_GAMMA_J-9: The system shall be able to restore 1000 records per second.

### 5.2 Safety Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system will do periodic backups through a live internet connection.

### 5.3 Security Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system shall validate credit cards against fraud.

## Requirement 2

REQ-0000_-_GAMMA_J-2: The system shall encrypt all sensitive information via https.

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system shall encrypt all customer data in database.

## Requirement 4

REQ-0000_-_GAMMA_J-4: The system shall auto detect IP DOS attacks and block IP automatically.

## Requirement 5

REQ-0000_-_GAMMA_J-5: The system shall detect consecutive failed login attempts.

## Requirement 6

REQ-0000_-_GAMMA_J-6: The system shall be protected by open source firewall called Firestarter. http://www.fs-security.com/

### 5.4 Availability Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system shall have an availability of 99.99%.

### 5.5 Efficiency Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system shall perform searches via Dijkstra's shortest path algorithm.

## Requirement 2

REQ-0000_-_GAMMA_J-2: For returning customers, the system shall validate 'existing' credit card in system after each log in.

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system shall automatically compress image files that are too large in size.

## Requirement 4

REQ-0000_-_GAMMA_J-4: The system will employ on demand asynchronous loading for faster execution of pages.

## Requirement 5

REQ-0000_-_GAMMA_J-5: The system shall validate email address existence.

### 5.6 Usability Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system shall be easy to use

## Requirement 2

REQ-0000_-_GAMMA_J-2: The system shall be easy to learn

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system shall utilize help bubbles to assist managers, customers, and administrators

## Requirement 4

REQ-0000_-_GAMMA_J-4: The system shall employ easy to locate buttons

## Requirement 5

REQ-0000_-_GAMMA_J-5: The system shall prompt customer with friend easy to read error messages.

## Requirement 6

REQ-0000_-_GAMMA_J-6: The system shall utilize consistent symbols and colors for clear notifications.

#### 5.7 Maintainability Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system shall utilize interchangeable plugins.

## Requirement 2

REQ-0000_-_GAMMA_J-2: The system shall be easily updatable for fixes and patches.

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system shall create logs of all changes, updates, or fixes that are done to the site.

## Requirement 4

REQ-0000_-_GAMMA_J-4: The system shall be easy to upgrade.

#### 5.8 Portability Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system shall be extremely portable via the usb drive.

## Requirement 2

REQ-0000_-_GAMMA_J-2: The system shall be easy to migrate or backed up via another usb drive.

#### 5.9 Testability Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system should be able to run under debug mode.

## Requirement 2

REQ-0000_-_GAMMA_J-2: The system should be able to run test credit card transactions.

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system should be able to run test shipping orders.

## Requirement 4

REQ-0000_-_GAMMA_J-4: The system should be able to create test environment of weborder system.

## 6 Other Requirements

## Requirement 1

REQ-0000_-_GAMMA_J-1: The system hardware shall be fixed and patched via an internet connection.

## Requirement 2

REQ-0000_-_GAMMA_J-2: Yoggie shall coordinate on future enhancement and features with our organization.

## Requirement 3

REQ-0000_-_GAMMA_J-3: The system shall adhere to the following hardware requirements: 4GB Flash ram chip 128MB SDRAM Intel XScale PXA270 520-MHz chipset OS: Apache web server Database: MySQL

## Glossary

## Appendix B: Use Cases

### Customer Use Cases

#### Register Customer

##### Goal

Register a new customer account with the system.

##### Actors:

Customer Weborder System

##### Preconditions:

Customer must be able to access the web order system via a web browser with HTTPS.

##### Triggers:

Customer clicks button or link to "Register"

##### Basic Scenario:

Customer first clicks on the button or link to initiate registration process. System prompts the customer to fill out his/her first name, last name, billing address, shipping address, email address, and their password. Customer enters fields. System validates the customer's information. System creates a new account for the Customer. System creates a session cookie. System displays an account home page to Customer.

##### Alternative Scenario:

A1. System recognizes Customer's cookie. A2. Go to Step 7 (Basic Scenario).

##### Postconditions:

The Customer registers and creates a new customer account with the system.

#### Login Customer

##### Goal

Login to a customer account with the system.

##### Actors:

Customer Weborder System

##### Preconditions:

Customer account must already be registered.

##### Triggers:

Customer clicks button or link to "Login"

##### Basic Scenario:

Customer clicks on the button or link to initiate the login process. 2. System prompts the customer for his/her email and password. System verifies the information. System creates session cookie. System displays account home page to the Customer

##### Alternative Scenario:

A1. System recognizes the Customer's cookie A2. Go to Step 5 (Basic Scenario). B1. Customer enters incorrect login information. B2. System prompts the Customer to resend login details to the email account. B3. Customer confirms. B4. System sends an email to the registered email address. B5. Go to Step 1 (Basic Scenario).

##### Postconditions:

The Customer is logged into the system.

#### Edit Customer Details

##### Goal

Edit the customer account details.

##### Actors:

Customer Weborder System

##### Preconditions:

Customer must be logged-in on the system.

##### Triggers:

Customer clicks on the button or link to "Edit Account"

##### Basic Scenario:

Customer clicks the button or link to initiate the process to edit the account. 2. System displays the account home page to the Customer. Customer clicks the button or link in order to edit the account details. System verifies the changes. System stores new account information.

##### Alternative Scenario:

None

##### Postconditions:

The Customer has changed the account details.

#### Logout Customer

##### Goal

Logout the customer account on the system.

##### Actors:

Customer Weborder System

##### Preconditions:

Customer must be logged-in on the system.

##### Triggers:

Customer clicks on the button or link to "Logout"

##### Basic Scenario:

Customer clicks the button or link in order to initiate logout process. System terminates the session cookie. System displays the home page.

##### Alternative Scenario:

None

##### Postconditions:

The Customer is logged out of the system.

#### Add Item To Cart

##### Goal

Customer adds item(s) in the cart

##### Actors:

Customer Weborder System

##### Preconditions:

The customer must be logged-in on the system.

##### Triggers:

Customer clicks the button or link to "Add To Cart".

##### Basic Scenario:

Customer clicks the button or link in order to add to the cart with specified quantity. 2. System adds the item(s) to the cart. System prompts the Customer to edit the quantity or remove the item from cart. Customer confirms the items in the cart. System stores cookie with cart details. Customer returns to product listings.

##### Alternative Scenario:

A1. Customer terminates the web browser window after adding item(s) to cart. A2. Customer returns to weborder interface. A3. System recognizes cookie and goes to step 6 (Basic Scenario) with existing items in cart.

##### Postconditions:

The Customer has added item(s) to the shopping cart.

#### Checkout An Order

##### Goal

Customer places and confirms an order for the checkout process.

##### Actors:

Customer Weborder System

##### Preconditions:

Customer must be logged-in on the system. Customer must have item(s) in the shopping cart.

##### Triggers:

Customer clicks button or link to "Ckeckout"

##### Basic Scenario:

Customer clicks the button or link to initiate the checkout process. System calculates order of items in the shopping cart. System appends cookie with flag for checkout process. System presents the customer with the account details and payment methods. 5. Customer confirms account details and payment methods. Customer confirms order. System stores order confirmation and order details. System sends email confirmation to the Customer. System appends cookie with flag for completed checkout process.

##### Alternative Scenario:

A1. Customer terminates order web browser during order the checkout process. A2. Customer returns to weborder interface. A3. System recognizes cookie and goes to step 4 (Basic Scenario).

##### Postconditions:

The Customer has placed and confirmed an order.

### Administrator Use Cases

#### Login Administrator

##### Goal

Login to an Administrator account with the system.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator account must already be registered.

##### Triggers:

Administrator clicks button or link to "Login"

##### Basic Scenario:

Administrator clicks button or link to initiate login process. System prompts the Administrator for email and password. System verifies information. System creates session cookie. System displays account home page to Administrator

##### Alternative Scenario:

A1. System recognizes Administrator 's cookie A2. Go to Step 5 (Basic Scenario). B1. Administrator enters incorrect login information. B2. System prompts Administrator to resend login details to email account. B3. Administrator confirms. B4. System sends email to registered email address. B5. Go to Step 1 (Basic Scenario).

##### Postconditions:

The Administrator is logged into the system.

#### Logout Administrator

##### Goal

Logout the Administrator account on the system.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be logged-in on the system.

##### Triggers:

Administrator clicks button or link to "Logout"

##### Basic Scenario:

Administrator clicks button or link to initiate logout process. System terminates the session cookie. System displays home page.

##### Alternative Scenario:

None

##### Postconditions:

The Administrator is logged out of the system.

#### Add User

##### Goal

Register a new customer, sales person, or administrator account with the system

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to "Add Users"

##### Basic Scenario:

Administrator clicks the button or link to initiate Add user process. System prompts the Administrator to fill out first name, last name, username, email address, password, and privileges of the user. System validates new user information. System creates a new account for the new user with desired privileges. System displays account home page to Administrator.

##### Alternative Scenario:

None

##### Postconditions:

A new customer account is created within the system.

#### Remove User

##### Goal

Remove a user from the system.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to “Remove User"

##### Basic Scenario:

Administrator clicks button or link to initiate the remove user process. System prompts the Administrator to select a user by searching or viewing a list of users. System displays user information. System confirms deletion of selected user. System displays account home page to Administrator.

##### Alternative Scenario:

None

##### Postconditions:

An account has been deleted within the system.

#### Change User Properties

##### Goal

Alter properties such as passwords and privileges of the user.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to “Change User Properties"

##### Basic Scenario:

Administrator clicks the button or link to initiate change user properties process. System prompts the Administrator to select a user by searching or viewing a list of users. System displays the user information. System alters the user properties. System displays the account home page to Administrator.

##### Alternative Scenario:

None

##### Postconditions:

An account has been altered within the system.

#### Install Plug-ins

##### Goal

Install a new plug-in to the application.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks the button or link to "Install Plug-ins "

##### Basic Scenario:

Administrator clicks the button or link to initiate Plug-in installation process. System prompts the Administrator to upload the Plug-in module. System installs plug-in and validates changes. System displays plug-in options to the Administrator.

##### Alternative Scenario:

None

##### Postconditions:

A new plug-in is installed in the application.

#### Remove Plug-ins

##### Goal

Remove a plug-in from the application.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks the button or link to "Install Plug-ins"

##### Basic Scenario:

Administrator clicks the button or link to initiate Plug-in deletion process. System prompts the Administrator to select the desired Plug-in module. System removes the plug-in and validates changes.

##### Alternative Scenario:

None

##### Postconditions:

A plug-in is removed from the application.

#### Manage Plug-in Options

##### Goal

Make changes to an installed plug-in.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to "Manage Plug-ins "

##### Basic Scenario:

Administrator clicks the button or link to initiate Plug-in Options process. System prompts the Administrator to select the desired Plug-in module. System displays all plug-in options to the Administrator. System confirms changes with the Administrator.

##### Alternative Scenario:

None

##### Postconditions:

A plug-in’s options have successfully been changed.

#### Install patch process

##### Goal

Install patches or software updates to the web store.

##### Actors:

Administrator Weborder System

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks the button or link to "Install Patch"

##### Basic Scenario:

Administrator clicks the button or link to initiate Patching process. System prompts the Administrator to upload the patch. System automatically installs patches and reinitializes software. System confirms that patch has been successfully installed.

##### Alternative Scenario:

None

##### Postconditions:

The web store was successfully updated.

### Sales Person Use Cases

#### Login Sales Person

##### Goal

Login to an account with the system.

##### Actors:

Sales Person Weborder System

##### Preconditions:

Sales Person account must already be registered.

##### Triggers:

Sales Person clicks button or link to "Login"

##### Basic Scenario:

Sales Person clicks the button or link to initiate login process. System prompts the Sales Person for email and password. System verifies the information. System creates session cookie. System displays the account home page to Sales Person

##### Alternative Scenario:

A1. System recognizes Sales Person's cookie A2. Go to Step 5 (Basic Scenario). B1. Sales Person enters incorrect login information. B2. System prompts the Sales Person to resend login details to email account. B3. Sales Person confirms. B4. System sends email to registered email address. B5. Go to Step 1 (Basic Scenario).

##### Postconditions:

The Sales Person is logged into the system.

#### Logout Sales Person

##### Goal

Logout the Sales Person account on the system.

##### Actors:

Sales Person Weborder System

##### Preconditions:

Sales Person must be logged-in on the system.

##### Triggers:

Sales Person clicks the button or link to "Logout"

##### Basic Scenario:

Sales Person clicks the button or link to initiate logout process. System terminates the session cookie. System displays home page.

##### Alternative Scenario:

None

##### Postconditions:

The Sales Person is logged out of the system.

#### Add Product

##### Goal

Add a product to the system.

##### Actors:

Sales Person Weborder System

##### Preconditions:

Sales Person must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Sales Person clicks the button or link to "Add Product"

##### Basic Scenario:

Sales Person clicks the button or link to initiate Add Product process. System prompts the Sales Person to fill out product name, product id, product description, product price, upload a product image, number of items in inventory, and availability of product. System validates the new product information. System creates a new product page for the new product. System displays the newly created product page.

##### Alternative Scenario:

None

##### Postconditions:

A new product is created within the system.

#### Remove Product

##### Goal

Remove a product from the system.

##### Actors:

Sales Person Weborder System

##### Preconditions:

Sales Person must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Sales Person clicks the button or link to "Remove Product"

##### Basic Scenario:

Sales Person clicks the button or link to initiate Remove Product process. System prompts the Sales Person to select a product by searching or viewing a list of products. System validates the product information. System removes the product page and product information from the system. System displays the newly created product page.

##### Alternative Scenario:

None

##### Postconditions:

A product is deleted from the system.

#### Update Product Attributes

##### Goal

Update Product attributes within the system.

##### Actors:

Sales Person Weborder System

##### Preconditions:

Sales Person must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Sales Person clicks the button or link to "Update Product Attributes"

##### Basic Scenario:

Sales Person clicks the button or link to initiate Update Product Attributes process. System prompts the Sales Person to select a product by searching or viewing a list of products. System displays all of the product attributes and allows Sales Person to update the product name, product id, product description, product price, update the product image, product availability, and/or the number of items in the inventory. System validates the product information. System updates the product page and product information within the system. System displays the newly updated product page.

##### Alternative Scenario:

None

##### Postconditions:

The product attributes have been changed.

## Appendix C: Analysis Models

None

## Appendix D: Issues List

Currently, telephonic orders are a significant source of business at Gamma-J which is both expensive and labor extensive. The organization has to figure out a way to have a smooth transition of orders coming in through telephones to the new online ordering system without loosing business to the competitor. Gamma-J depends mainly on Fed-Ex for its tracking number and transportation needs to ship the orders. A separate module to generate the tracking numbers and having a transportation system will be considered in the future. System does not support customer order analysis.

## Appendix E: Data Dictionary

User ID = User ID of the employee /customer of Tool Co Company; minimum 4 to maximum 10 characters (alphabetic or alphanumeric) Password = Password of the employee /customer of Tool Co Company; minimum 4 to maximum 10 characters (alphabetic or alphanumeric) Item name = Name of the selected item; maximum 50 character alphabetic string Item ID = ID that uniquely identified the selected item; a 7-digit system generated alphanumeric character Price = Cost of a single unit of the selected item; in dollars and cents. Text description = special description of the selected item; maximum 100 alphabetic characters Shipping price = Cost for shipping the item to its destination; in dollars and cents Quantity = the number of units of each selected item that the customer is ordering; default = 1; maximum = quantity presently in inventory Total = Cost of a single unit of the selected item Number of units of that item selected; in dollars and cents Name = Name of the customer; maximum 100 alphabetic characters Address = Location of the customer City = Name of the city for the above address; maximum 20 characters alphabetic string State = Name of the state for the above city; maximum 20 characters alphabetic string Zip code = The postal code of the above address; 5 digit numeric string E-mail ID = E-mail address of the customer who is using the Web order system; 50 characters alphanumeric Credit Card No. = Credit card number of the customer; 16 digit numeric string Shipping address = Address where the item has to be shipped Credit card expiry date = The date on the credit card when it will get expired; format MM/YY Order No = Unique confirmation number of the order to the customer; 9 characters alphanumeric Tracking No. = Number to track the order; 20 characters alphanumeric Shipping date = Date when the specified order is shipped; format MM/DD/YYYY Location = Place where the item is kept in the warehouse in the form of (aisle, column, shelf)
