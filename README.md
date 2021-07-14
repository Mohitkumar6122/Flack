# Flack

A Slack like online messaging service


[![python badge](https://img.shields.io/badge/uses-python3-informational)](https://shields.io/) [![hrml5 badge](https://img.shields.io/badge/uses-html5-informational)](https://shields.io/) [![css badge](https://img.shields.io/badge/uses-css-informational)](https://shields.io/) [![SocketIO](https://img.shields.io/badge/uses-SocketIO-informational)](https://shields.io/) [![flask badge](https://img.shields.io/badge/uses-flask-informational)](https://shields.io/) [![SQLAlchemy](https://img.shields.io/badge/uses-SQLAlchemy-informational)](https://shields.io/) 
[![Heroku](https://heroku-badge.herokuapp.com/?app=flack-ap)](https://www.heroku.com/) 


## Summary
[Flack](https://flack-ap.herokuapp.com/) is a messaging platform like [Slack](https://slack.com/) that allows users to message in real time. Current features includes registering an account, adding or removing message channels, adding or removing users to channels and sending messages in desired channels. For messaging, [Flask-SocketIo](https://flask-socketio.readthedocs.io/en/latest/) library is used. 

## Files Structure
```bash
Flack
├── config.py
├── flack
│   ├── application.py
│   ├── forms.py
│   ├── __init__.py
│   ├── models.py
│   ├── static
│   │   ├── images
│   │   │   ├── demo.gif
│   │   │   ├── favicon-people-arrows.ico
│   │   │   └── man-silhouette-profile-7.png
│   │   ├── scripts
│   │   │   ├── chat.js
│   │   │   ├── lib.js
│   │   │   └── socket.js
│   │   └── styles
│   │       ├── chat.css
│   │       └── layout.css
│   └── templates
│       ├── chat.html
│       ├── helper.html
│       ├── index.html
│       ├── layout.html
│       ├── login.html
│       └── temp.html
├── Procfile
├── README.md
└── requirements.txt

```
## File descriptions
* ```/flack```: the main app module
* ```application.py```: the main application file containing the logic for registering, login, logout, and other API calls such as adding/removing channels.
* ```forms.py```: contains the classes for registration form and login in form which uses the Flask-WTForms library.
* ```models.py```: Uses Flask SQLAlchemy to abstract away the database tables and there relationships. Models include User, Channel, and Message.
* ```/templates```: contains all the HTML files to render different views.
* ```/script```: contains all the JavaScript files to run the client side code.
* ```/styles```: contains all the CSS files for styling.
* ```requirements.txt```: contains all the Python packages installed for this project and also this file is required for Heroku.
* ```Procfile```: a file required for heroku.



## Usage
### Running the app:
[Use this link to run the live app directly](https://flack-ap.herokuapp.com/)

### Cloning and editing
* After cloning, replace the secret key (i.e modify the line ```SECRET_KEY = os.environ.get('SECRET_KEY')```) and the Database URL (i.e the line ```SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')```) in ```config.py``` with your own values. 

### Running Project
First of all you have to prepare your virtual environment. Select
a location where you want to store the files and follow the following steps.
```
    mkdir Projects
    cd Projects
    git clone https://github.com/Mohitkumar6122/Flack.git
    python3 -m venv virtenv
    source venv/bin/activate
    pip install -r requirements.txt
    python applications.py
```
It will create a Projects Folder which will contain all files of project.
Then after running applications.py. A chrome window will open which contains a interacive window where app will be running.