from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config
from .applications import *

# Configure the flask app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)

# Initialize the data base
db = SQLAlchemy(app)
# Initialize the password hashing object
bcrypt = Bcrypt(app)
# Initialize flask web socketIO
socketio = SocketIO(app)

# Configure the flask login Manager
login_manager = LoginManager()
login_manager.init_app(app)
# The name of the view to redirect to when the user needs to log in
login_manager.login_view = "login"
login_manager.login_message_category = "danger"


from .models import User, Message, Channel
db.create_all()
db.session.commit()

# create the initial channels
if (not Channel.query.filter_by(name="general").first()):
    channelGeneral = Channel(name="general", is_private=False)
    db.session.add(channelGeneral)
    db.session.commit()

if (not Channel.query.filter_by(name="other").first()):
    channelOther = Channel(name="other", is_private=False)
    db.session.add(channelOther)
    db.session.commit()
