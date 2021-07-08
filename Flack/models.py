from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from flack import db, bcrypt

# association table. Links users to channels
user_channel_link = db.Table('user_channel_link',
                             db.Column('user_id', db.Integer, db.ForeignKey(
                                 'users.id', ondelete='CASCADE'), primary_key=True),
                             db.Column('channel_id', db.Integer, db.ForeignKey(
                                 'channels.id', ondelete='CASCADE'), primary_key=True)
                             )


class User(db.Model, UserMixin):
    """  User model. Represents the table "users" """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    sid = db.Column(db.String())
    messages = db.relationship(
        "Message", cascade="all, delete-orphan", backref=db.backref("user", lazy=True))
    channels = db.relationship("Channel", secondary=user_channel_link, lazy=True, passive_deletes=True, cascade="all,delete",
                               backref=db.backref("users", lazy=True))

    @property
    def password(self):
        """
            prevents accessing the plaintext password

        Raises:
            AttributeError: password not readable
        """
        raise AttributeError('password not readable')

    @password.setter
    def password(self, plaintext):
        """
            Hashed the plaintext passwords and stores it in the database
            Bcrypt library is used to hash the password.

        Args:
            plaintext (string): the plaintext unhashed password.
        """
        # decode utf is used with python-3 
        self.password_hash = bcrypt.generate_password_hash(
            plaintext).decode("utf-8")

    def verify_password(self, plaintext):
        """
            Verify if the input plaintext password with this objects hashed password matches or not.
            Bcrypt library is used to perform this check.

        Args:
            plaintext (string): password string unhashed

        Returns:
            boolean: returns true if the hashed password field of the calling object matches with the unhashed
                plaintext password and false otherwise
        """
        return bcrypt.check_password_hash(self.password_hash, plaintext)

    def add_message(self, msg, channel_id):
        """
            creates a new message in database and commits the addition.
            Also adds this message to the list "messages" for the calling user (But Why? 
            don't we have to manually do self.messages.add(new_msg)?)

        Args:
            msg (string): the message content
            channel_id (string): the name the channel this message belongs to

        Returns:
            [type]: [description]
        """
        new_msg = Message(message=msg, user_id=self.id, channel_id=channel_id)
        db.session.add(new_msg)
        db.session.commit()
        return new_msg


class Channel(db.Model):
    """ Channel Model. Used as an abstraction for the "channels" table.
        Each Channel has a many to many relationship with users. Thus each
        channel can access its users using "<A_Channel_Object>.users"
    """
    __tablename__ = "channels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    is_private = db.Column(db.Boolean, default=True, nullable=False)
    messages = db.relationship(
        "Message", cascade="all, delete-orphan", backref=db.backref("channel", lazy=True))


class Message(db.Model):
    """ Message Model. Used as an abstraction for the "message" table.
        Each message is assigned to a user and can be accessed by "<A_Message_Object>.user"
        Each message is assigned a channel and can be accessed by "<A_Message_Object>.channel"
    """
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey(
        "channels.id"), nullable=False)

