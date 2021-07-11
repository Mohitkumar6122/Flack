// function which returns true if a user is added
// else returns false (if no user is left to add to the channel)
function addUsersOptions() {

    let isUpdated = false;
    const activeChannelUsers = JSON.parse(localStorage.getItem("activeChannelUsers"));
    const users = $("#get_all_users").data("users");
    // console.log(users);
    $("#users_to_add_selected").html("");

    for (let i = 0; i < users.length; i++){

        if (!activeChannelUsers.includes(users[i])){
          $("#users_to_add_selected").append(
            "<option>" + users[i] + "</option>"
          );
          //  use the refresh method to update the UI to match the new state.
          $("#users_to_add_selected").selectpicker("refresh");
          isUpdated = true;
        }
    }
    
    return isUpdated;
}

// update the tooltip for user add button for the active channel. If all users are already
// added to the active channel, then it disables the button to add more users
function updateUserTooltip() {

    // add user options in multiselect dropdown in the modal that pops up when add user button
    // is pressed. If no users is added, i.e addUsersOptions() returns false, then disable the 
    // add user button and update the tooltip
    if (!addUsersOptions()){

        $("#add_users span").prop("disabled", true);
        $("#add_users_btn").prop("disabled", true);
        $("#add_users_btn_wrapper").attr('data-original-title', "All users already in this channel");
    }else{

        $("#add_users span").prop("disabled", false);
        $("#add_users_btn").prop("disabled", false);
        $("#add_users_btn_wrapper").attr('data-original-title', "Click to add users");
    }
}

function getUsersInChannel(){
    const users = JSON.parse(localStorage.getItem("activeChannelUsers"));
    let text = "<p>This channel has users:"
    
    for (let i = 0; i < users.length; i++){
        text += "<br>" + users[i]
    }

    text += '<\p>';
    return text;
}


// creates the html to display the message based on the dictionary data
function displayMessage(data){ 

    let lastDate = $("#message_section").children(".date").last();
    let date = '';

    if (lastDate.length != 0){
        // trying to get the text inside the span
        lastDate = lastDate.children().html();
    }

    if (lastDate != data.date){
        date += '<div class="date"><span>' + data.date + '</span></div>';
    }


    let message =   '<div class="message-container"> \
                        <img src="./static/images/man-silhouette-profile-7.png" alt="Avatar" class="avatar"> \
                        <div class="message-text-container"> \
                            <span class="username">' + data.username  + '</span> \
                            <span class="time">' + ' ' + data.time + '</span> \
                            <br>' + 
                            data.msg + 
                        '</div> \
                    </div>'; 
                    

    $("#message_section").append(date + message);

}

function removeUserFromStorage(user){
    let activeChannelUsers = JSON.parse(localStorage.getItem("activeChannelUsers"));
    let i = activeChannelUsers.findIndex(username=>username===user);

    if (i != -1){
        activeChannelUsers.splice(i, 1);
        // after updating activechannelusers store it in local storage
        localStorage.setItem("activeChannelUsers", JSON.stringify(activeChannelUsers));
    }
}