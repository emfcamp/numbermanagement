# Thats numberwang!

## Overview

This is a new number management app for the EMF Phone Team at Events,
The goal of the app is to allow users to regsiter custom extensions and get appropriate credentials or configuration to use those with different Types of Service (DECT, SIP, Cellular, POTS etc)

It will then expose provisioning feeds to the telephone systems to create the relevent configuration based on the ToS.

The aim it to make the platform configurable to support multiple new ToS without requiring code changes, eg if someone wants to stand up a pager system and admin can then create a new ToS.

## Role Based Access Control

Admin - Has elevated privileges to configure the system (this is using the django admin interface)
Operator - Has privileges to assign permissions to users, modify user services and allocate privileged numbers
User - Regular user, can create and update their own extensions and service parameters 
Guest - Unregistered user, can view some public information such as directory.

## Features
## WebApp
- As an Admin I want to be able to create types of service eg DECT, SIP, POTS, Cellular etc.
- As an Admin I want to be able to assign parameter fields to a Type of service
- As an Admin I want to be able to define available number ranges for users to register from
- As an Admin I want to be able to define permission flags for extensions  (external, international etc)
- As an Admin I want to be able to designate users as operators
- As a User I want to be able to register an account
- As a User I want to be able to register a number from the available ranges with a type of service
- As a User I want to be able to choose if my number appears in the phonebook
- As a User I want to be able to delete one of my numbers
- As a Guest I want to be able to view the phonebook
- As an Operator I want to be able to assign a number to any user including privileged ranges and ToS
- As an Operator I want to be able to assign permissions to an extension
- As an Operator I want to be able to delete an extension from a User
- As an Operator I want to be able to ban a User
- As an Operator I want to be able to bar a number
- As a User I want to be able to be able to reset my password
- As a user I want to be able to update my name, email or password (username is fixed)
- As a user I want to verify my email when I signup

### API 
- As an app I want to be able to fetch all config for a given ToS
- As an Admin I want to be able to create API Keys
- As an Admin I want to limit API keys scope by ToS


## Running Locally

The application is built in django, for development purposes it uses a local sqlite3 database that is created by django
The only requirement currently is Python 3, Django 5.0 or later and the django-extensions package for clearing the database, other requirements may be added to the `requirements.txt` file as the project develops.

- Clone this repository

	`git clone https://github.com/emfcamp/numbermanagement`

- Enter directory

	`cd nms`

- Install requirements 

	`pip install -r requirements.txt`

- Rename the example.env file, (you should be fine with dummy values in there if you're not sending provisioning messages to the phone system.)

	`mv example.env .env`

- First time you will likely want to clean and setup the database, Either:

	- run `bash ./clean_setup_db.sh` (which does all of the below for you)

	- OR run the following commands 
		
		```
		python manage.py reset_db
		ls -R */migrations/000*.py | xargs rm 
		python manage.py makemigrations
		python manage.py migrate
		```

		This will leave you with an empty database, if you want to populate the db with some sample data run
		
		`python manage.py loaddata fixture.json`
	
	This adds 3 users to the platform, `user` `operator` % `admin` all with the password of `numberwang`
	
	You will also have an active event called development, Groups, DECT, SNOM & POTS type of service and some sample numbers.


- Start the dev server
`python manage.py runserver`

	Should now be running on localhost:8000

	You can access the admin interface on /admin
