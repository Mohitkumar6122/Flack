$(document).ready(function() {
    // initialize some global variables
    let activeChannelName = localStorage.getItem("activeChannelName");
    let activeChannelUsers = JSON.parse(
        localStorage.getItem("activeChannelUsers")
    );
    const sendButton = $("#send_message");

    const users = $("#get_all_users").data("users");

    // update the active channel information to be displayed. If no active channel stored in the
    // local storage then save and show the general channel
    updateChannelDisplay();

    // update the header to display the active channel
    document.querySelector("#curr_channel").firstElementChild.innerHTML =
        "#" + activeChannelName;
    // make an ajax request to get the channel messages and current users in this channel and
    // update the display accordingly

    getMessages(activeChannelName);
    // since nothing is typed this moment, make sure to prevent sending message
    sendButton.disabled = true;

    // allow enter to result in sending message only if the typed message is not empty
    $("#user_message").on("keyup", function(event) {
        const inputMessage = $("#user_message");

        if (inputMessage.val().length > 0) {
            $("#send_message").prop("disabled", false);
        } else {
            $("#send_message").prop("disabled", true);
        }

        if (inputMessage.val().length > 0 && event.keyCode === 13) {
            sendButton.click();
        }
    });

    $("#new_channel_name").on("keyup", function(event) {
        if ($("#new_channel_name").val().length > 0) {
            $("#create_channel_btn").prop("disabled", false);
            $("#channelHelp").css("visibility", "hidden");
        } else {
            $("#create_channel_btn").prop("disabled", true);
        }
    });

    // make the clicked channel to be active one, calling ajax request to retrieve the
    // message for selected channel. Update tooltips and disable the user button if all
    // users are already in this channel
    $("#channels").on("click", function(event) {
        if (
            event.target &&
            (event.target.nodeName == "A" || event.target.nodeName == "LI")
        ) {
            let parentElem = $(event.target.parentNode);
            // prints the channel name which is clicked
            // console.log(parentElem.data("channel"));

            if (event.target.id == "leave") {
                leaveChannel(parentElem.data("channel"), false);
                // ajax request to leave the group
            } else if (event.target.id == "delete") {
                leaveChannel(parentElem.data("channel"), true);
            } else {
                let activeChannel = document.querySelector("li.active");
                activeChannel.classList.remove("active");

                if (event.target.nodeName == "A") {
                    event.target.parentNode.classList.add("active");
                } else {
                    event.target.classList.add("active");
                }

                activeChannelName = localStorage.getItem("activeChannelName");
                channelSelected = event.target.innerText || event.target.textContent;
                // console.log(channelSelected);
                // console.log(channelSelected.length);

                if (activeChannelName != channelSelected) {
                    // console.log(activeChannelName);
                    localStorage.setItem("activeChannelName", channelSelected);
                    document.querySelector("#curr_channel").firstElementChild.innerHTML =
                        "#" + channelSelected;
                    getMessages(channelSelected);
                    activeChannelName = channelSelected;
                }

                document.querySelector("#user_message").focus();
            }
        }
    });

    // if active channel name or channel users have not yet being stored (i.e first time running the script)
    // set it to the first channel in list of channels (the channel "#general")
    // else set the active channel from the stored one and update the count of users in this channel
    function updateChannelDisplay() {
        if (
            !activeChannelName ||
            !activeChannelUsers ||
            $("#" + activeChannelName).length === 0
        ) {
            $("#channels").children(":first").addClass("active");
            localStorage.setItem("activeChannelName", $("li.active a").html());
            activeChannelName = localStorage.getItem("activeChannelName");
            localStorage.setItem("activeChannelUsers", JSON.stringify(users));
            activeChannelUsers = JSON.parse(
                localStorage.getItem("activeChannelUsers")
            );
        } else {
            $($("#" + activeChannelName)).addClass("active");
            $("#num_users a span").html(activeChannelUsers.length);
        }
    }

    function leaveChannel(channel, isToBeDeleted) {
        $.ajax({
            url: "chat/leave_channel", // to the "leave_channel" view in app__.py
            type: "POST",
            data: JSON.stringify({
                channel: channel,
                isToBeDeleted: isToBeDeleted
            }),
            contentType: "application/json; charset=utf-8", // sends in format
            dataType: "json", // recieves in the format

            success: function(data) {
                if (data.success) {
                    if (activeChannelName === data.channel) {
                        $("#" + data.channel).removeClass("active");
                        const nextChannel = $("#" + data.channel).next();
                        const nextActiveChannel =
                            nextChannel.length === 0 ?
                            $("#" + data.channel).prev() :
                            nextChannel;
                        localStorage.setItem(
                            "activeChannelName",
                            nextActiveChannel.children("a").html()
                        );
                        activeChannelName = localStorage.getItem("activeChannelName");
                        $($("#" + activeChannelName)).addClass("active");
                    }
                    // delete the channel
                    $("#" + data.channel).remove();

                    $("#curr_channel a").html("#" + activeChannelName);
                    getMessages(activeChannelName);
                } else {
                    // do nothing AJAX failed
                    // alert("Request Failed");
                }
            },
        });
    }

    function getMessages(channel) {
        $.ajax({
            url: "messages",
            type: "POST",
            data: JSON.stringify({
                channel: channel
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",

            success: function(data) {
                if (data.success) {
                    $("#message_section").html("");

                    for (let i = 0; i < data.entries.length; i++) {
                        displayMessage(data.entries[i]);
                    }

                    localStorage.setItem(
                        "activeChannelUsers",
                        JSON.stringify(data.users)
                    );
                    activeChannelUsers = JSON.parse(
                        localStorage.getItem("activeChannelUsers")
                    );
                    $("#num_users a span").html(activeChannelUsers.length);
                } else {
                    // AJAX Failed
                    // alert('Error :(');
                }
            },
        });
    }
});