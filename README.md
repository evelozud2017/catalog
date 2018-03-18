# Item Catalog App
Item Catalog App is a simple website application that displays a list of items within different categories.  It provides a user registration and authentication using third party system (Google Accounts).  Registered users will have the ability to add, update and delete items.

# Installation
1. Clone the vagrant installation from [github repository] https://github.com/udacity/fullstack-nanodegree-vm
2. Download the files including subfolders from this repository and copy it under catalog folder.
3. Prepare the environment: 
- Install the Virtual machine Vagrant and VirtualBox.  Instructions provided by [Udacity](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/bc51d967-cb21-46f4-90ea-caf73439dc59/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0)
- Launch the Vagrant VM `vagrant up`
- Login to vagrant `vagrant ssh`
3. Create and pre-populate the database:
- In vagrant, go to the catalog directory `cd /vagrant/ssh`
- Run the db setup `python itemcatalog_dbsetup.py`. This should create the itemcatalog.db
- Populate the tables by running `python loadtestdata.py`

# Code
This consists of the following:
- application.py - main python code that has logic for the website
- itemcatalog_dbsetup.py - python code that will create the itemcatalog.db
- loadtestdata.py - python code that will read from json file and populate the itemcatalog.db
- testdata.json - json file that has default user, categories and items
- static/bootstrap.min.css - stylesheet for bootstrap
- static/style.css - custom style for the website
- templates/additem.html - html page for adding new item
- templates/catalog.html - html page that will display the list of categories and latest added items after registered users logs in
- templates/catalogitems.html - html page that will display the list of items for the selected category
- templates/deleteitem.html - html page for deleting item. 
- templates/edititem.html - html page for updating item.
- templates/header.html - header section that will be displayed
- templates/itemdetail.html - html page that will display description. it will also show edit and delete links if the logged in user owns that item
- templates/login.html - html page for login
- templates/main.html - main page of website
- publiccatalog.html - html page that will display the list of categories and latest added items. This will be view only

# How to use
Run the python application.py

# How to run code
1. Inside vagrant in /vagrant/catalog, run the application `python application.py`
2. Open the browser and goto http://localhost:8000/


# Technologies used
- PYTHON
- BOOTSTRAP
- FLASK
- SQLALCHEMY
- OAUTH 2.0 to access Google APIs 
- VAGRANT

License
----

MIT


