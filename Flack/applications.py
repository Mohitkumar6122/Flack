import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import emit, send, join_room, leave_room
from datetime import datetime
from .forms import *
from .models import *
from flack import db, app, login_manager, socketio


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/chat", methods=["Get"])
@login_required
def chat():
    """
        Chat route. Requires the user to be logged in before accessing 
        this route. Achieved through login_required decorator. Renders 
        the chat html page passing in the current registered users and the channel
        the current user(user that made the GET request) is part of.
    """
    user_channels = [channel.name for channel in current_user.channels]
    users = [user.username for user in User.query.all()]

    return render_template("chat.html", users=users, channels=user_channels)


@app.route("/", methods=["Get", "Post"])
def index():
    """
        Index (root) page route. Renders an registration page with empty 
        registration form on GET and adds the username and password
        to database on POST upon successful validation. All newly registered
        users are also added to two public channels, "general" and "other".
        Finally redirects to login page once users has successfully registered.
    """

    reg_form = RegistrationForm()

    # for post requests
    if reg_form.validate_on_submit():
        # get the inputted fields from the form
        username = reg_form.username.data
        password = reg_form.password.data

        # add the user to the db
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # add newly registered user to all public channels
        for channel in Channel.query.filter_by(is_private=False):
            join_msg = "Joined" + "#" + channel.name
            new_user.add_message(msg=join_msg, channel_id=channel.id)
            new_user.channels.append(channel)
            channel.users.append(new_user)

        db.session.commit()

        flash("Registered successfully! Please Log In", "success")
        return redirect(url_for("login"))

    return render_template("index.html", form=reg_form)


@app.route("/login", methods=["Get", "Post"])
def login():
    """
        Login route. Renders the login page with empty 
        login form instance on GET request. Using flask login manager,
        the users is logged in on POST request when the form making the
        request is successfully validated.
    """

    login_form = LogInForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        login_user(user)
        return redirect(url_for("chat"))

    return render_template("login.html", form=login_form)


@app.route("/logout")
@login_required
def logout():
    """
        Logout route. Logout the users and redirect
        to the login page
    """

    logout_user()
    flash("Successfully logged out", "success")
    return redirect(url_for("login"))


@app.route("/messages", methods=["POST"])
def get_messages():
    """
        Returns a json object containing all messages and its
        relevant details for requested channel.
    Returns:
        json: has values with keys:
            - "entries": a dictionary of containing "msg" (the message content),
                 "time" (the message sent timestamp), "date" (the date message was sent)
            - "users": all the users in the requested channel
            - "sucess": a boolean to indicate the whether the api call was successful
    """
    data = request.get_json()
    channel_name = data["channel"]
    channel = Channel.query.filter_by(name=channel_name).first()

    entries = []

    for msg_obj in channel.messages:
        username = msg_obj.user.username
        msg_time = msg_obj.timestamp.strftime("%#I:%M %p")
        msg_date = msg_obj.timestamp.strftime("%A %B, %eth")
        entry = {"username": username, "time": msg_time,
                 "date": msg_date, "msg": msg_obj.message}
        entries.append(entry)

    users = [user.username for user in channel.users]

    return jsonify({"entries": entries, "users": users, "success": True})


@app.route("/chat/add_users", methods=["POST"])
def add_users():
    """
        An API call allows a client to add desired users to
        a requested channel. The users are also added to the
        room with same channel name to allow for sending and
        receiving real time messages in the room
    Returns:
        json: a key "success" is set true upon successfull
            execution of the client api call. 
    """

    data = request.get_json()
    usernames_to_add = data["users"]
    new_channel = Channel.query.filter_by(name=data["channel"]).first()

    for username in usernames_to_add:
        # find the user with this username in the db
        user = User.query.filter_by(username=username).first()
        # add the channel to this users channel list in database
        user.channels.append(new_channel)
        # add this new channel to the desired channel's users list. This does
        # not seem to be required as the above statement already takes care of this

        # if user is online then add the user to this channel using
        # socketio to receive message in real time
        if user.sid:
            socketio.server.enter_room(user.sid, new_channel.name)

        join_msg = "Joined" + "#" + new_channel.name

        msg_obj = user.add_message(msg=join_msg, channel_id=new_channel.id)
        # emit the join message to all the users in this new channel
        send_message(msg_obj, username, data["channel"])

    db.session.commit()

    # this tells the new user that he has been added so that now he can see this new channel right away
    socketio.emit("user added", {"username": current_user.username,
                  "channel": data["channel"]}, room=data["channel"])

    return jsonify({"success": True})


@app.route("/chat/create_channel", methods=["POST"])
def create_channel():
    """
        An API call that allows client to create new channels.
        Once a channel is created, the client who made the call
        is also added to this channel
    Returns:
        json: a key "success" whose value is set to true
            on successful execution of the API call and false otherwise
    """

    data = request.get_json()
    channel_name = data["channel"]

    if Channel.query.filter_by(name=channel_name).first():
        return jsonify({"success": False})

    new_channel = Channel(name=channel_name)
    db.session.add(new_channel)
    current_user.channels.append(new_channel)
    new_channel.users.append(current_user)
    db.session.commit()

    join_msg = "Joined" + "#" + channel_name
    current_user.add_message(msg=join_msg, channel_id=new_channel.id)

    return jsonify({"success": True})


@app.route("/chat/leave_channel", methods=["POST"])
def delete_channel():
    """
        An API call that allows clients to either delete a given
        channel or leave it. Only private channels can be deleted
    Returns:
        json: has values for keys:
            - "channel": the channel that client left or deleted
            - "success": a boolean that is set to true on successfull
                    execution of the API call
    """
    data = request.get_json()

    channel_leave = Channel.query.filter_by(name=data["channel"]).first()

    if not channel_leave:
        return jsonify({"success": False})

    if current_user.sid:
        socketio.server.leave_room(current_user.sid, data["channel"])

    if data["isToBeDeleted"] or (channel_leave.is_private and len(channel_leave.users) == 1):
        db.session.delete(channel_leave)
        db.session.commit()
    else:
        channel_leave.users.remove(current_user)
        leave_msg = "Left" + "#" + channel_leave.name
        msg = current_user.add_message(
            msg=leave_msg, channel_id=channel_leave.id)
        db.session.commit()

        send_message(msg, current_user.username, data["channel"])
        socketio.emit("leave channel", {
                      "username": current_user.username}, room=data["channel"])

    return jsonify({"success": True, "channel": data["channel"]})


def send_message(msg, username, channel_name):
    """
        A helper function that is used to emits/sends a message to 
        all users in the room named "channel_name"
    Args:
        msg (Model Class Object instance): the Message object that contains message details (see models.py)
        username (string): the name of the user to be attached to this message
        channel_name (string): the name of the channel/room in which this message is to be sent
    """

    msg_time = msg.timestamp.strftime("%#I:%M %p")
    msg_date = msg.timestamp.strftime("%A %B, %eth")
    socketio.send({"username": username, "msg": msg.message,
                   "time": msg_time, "date": msg_date, "channel": channel_name}, room=channel_name)


@socketio.on("message")
def message(data):
    """
        Function executed when the client sends a message event.

    Args:
        data (dictionary): has values for keys 
            - "msg": the message content send by the client
            - "channel": the channel in which this message was sent
    """

    selected_channel = Channel.query.filter_by(name=data["channel"]).first()

    assert (selected_channel != None)

    msg_obj = current_user.add_message(
        msg=data["msg"], channel_id=selected_channel.id)
    send_message(msg_obj, current_user.username, data["channel"])


@socketio.on('join channel')
def on_join(data):
    """
        Adds the current user to the passed channel name
        when "join channel" event is triggered
    Args:
        data (dictionary): has values for keys 
            - "channel" : the name of the channel to join
    """
    join_room(data['channel'])


@socketio.on("connect")
def on_connect():
    """
        adds the current users to all rooms (channels)
        that it belongs so that it can received socketio
        messages in realtime. Also stores the current
        user's sid to be later used when send direct
        messages between two users/clients
    """

    current_user.sid = request.sid
    db.session.commit()

    # once connected join all channels the user belongs to
    for channel in current_user.channels:
        join_room(channel.name)


if __name__ == "__main__":
    app.run()
