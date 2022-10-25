# MiRCommunication
In order to use MiR robot, a http communication is needed for connecting to the MiR rest API. This project in python
defines some required functions.

* * *
# Installation

In order to install the required libraries:

    $ pip install -r requirements.txt

* * *
# Auth file

Once you have the required libraries installed, fill the auth information in the auth_example.json.
The auth information can be seen in the MIR's dashboard -In this project the version 3.0.2 is being used. 
Go the Help menu and then to API documentation. Fill the API credentials and copy and paste the Authorization 
information in the field "auth" inside of the auth_example.json. Then change the name of this file as auth.json.

* * *

# Execution

In order to execute the code:

    $ python3 main.py
