import socket
import threading
import user
import channel

# initera socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '10.10.20.116'       # serveraddress
PORT = 12345  # serverport
QUEUE_SIZE = 5  # längd på kö för hantering av nya anslutningar

# registrera address och port för socket
s.bind((HOST, PORT))
s.listen(QUEUE_SIZE)

channels = {}
users = {}


def command_nickname(client_socket, command):
    users[client_socket].nickname = command[1]
    client_socket.send(("Nickname was successfully changed to: " + users[client_socket].nickname + "\n").encode())


def command_quit(client_socket, command):
    reason = command[1]  # Send to rest of chat
    client_socket.send("TERMINATE_CONNECTION".encode())  # Response to client
    print("Disconnected: " + str(users[client_socket].addr))  # Server Log
    users[client_socket] = None  # Remove User from list
    client_socket.close()


def command_send(client_socket, command):
    for i in channels[command[1]].userQueue:
        i.client_socket.send(command[2].encode())


def command_post(client_socket, command):
    pass


def command_kick(client_socket, command):
    pass


def command_join(client_socket, command):
    channel_exists = False
    try:
        tmp = channels[command[1]]
        channel_exists = True
    except KeyError:
        channel_exists = False

    if channel_exists:
        if channels[command[1]].userExists(users[client_socket]):
            client_socket.send("You are already in this channel!".encode())
        else:
            channels[command[1]].addUser(users[client_socket])
            client_socket.send(("Welcome user: "+ users[client_socket].nickname + " to channel: "+ channels[command[1]].channelName + "\nThe owner is:" + channels[command[1]].owner.nickname).encode())
    else:
        channels[command[1]] = channel.Channel(users[client_socket], command[1])
        channels[command[1]].addUser(users[client_socket])
        client_socket.send(("New channel with name:" + channels[command[1]].channelName + " Has been created!\nYou are the owner!").encode())


def command_part(client_socket, command):
    pass


def command_list(client_socket, command):
    pass


def command_noop():
    pass


def perform_command(client_socket, command):
    if command[0] == "NICK":
        command_nickname(client_socket, command)
    elif command[0] == "SEND":
        command_send(client_socket,command)
    elif command[0] == "KICK":
        command_quit(client_socket,command)
    elif command[0] == "JOIN":
        command_join(client_socket,command)
    elif command[0] == "LIST":
        command_list(client_socket, command)
    elif command[0] == "PART":
        command_part(client_socket,command)
    elif command[0] == "POST":
        command_post(client_socket,command)
    elif command[0] == "NOOP":
        command_noop()  # Does nothing


def get_data(client_socket):
    data = client_socket.recv(1024).decode("utf-8")
    return data


def translate_data_to_command(data):
    command_request = data.split(' ', 1)[0] # Only split the first call
    if command_request == "SEND":
        data = data.replace('SEND ', "")
        data = data.split(' :', 1)  # contains args for channel/username and the message
        data.insert(0, "SEND")
    elif command_request == "KICK":
        tmp = data.split(' :', 1)  # contains args for channel, username and reason
        data = tmp[0].split(" ")   # Splitting blank spaces only in the call commands
        data.append(tmp[1])  # Apply the reason back into the args
    elif command_request == "NICK" or command_request == "JOIN"\
        or command_request == "PART" or command_request == "LIST"\
            or command_request == "QUIT" or command_request == "NOOP":
        data = data.split(' :', 1)  # Call and argument can be seperated for the rest of commands
    else:
        data = "BAD_REQUEST"

    try:
        tmp = data[1]
    except KeyError:
        data = "MISSING_ARGS"

    print(data)  # log command on server
    return data


def check_quit_command(client_socket, command):
    if command[0] == "QUIT":
        command_quit(client_socket, command)
        return True
    else:
        return False


def request_nickname(client_socket):
    print(users)
    client_socket.send("Welcome to IRC chatt\n Please enter a nickname before joining any channel!\n".encode())
    while users[client_socket].nickname is None:  # Without a nickname it will not go further
        data = get_data(client_socket)
        command = translate_data_to_command(data)
        if command[0] == "NICK":
            nickname_taken = False
            for i in users:
                if users[i].nickname == command[1]:
                    nickname_taken = True
                    client_socket.send("Nick name is already taken".encode())
                    break
            if nickname_taken is False:
                command_nickname(client_socket, command)
        else:
            client_socket.send("Please enter a nick name...\n".encode())


def request_channel_join(client_socket):
    client_socket.send("Welcome to IRC chatt\nPlease start by joining a channel\n".encode())
    while True:
        data = get_data(client_socket)
        command = translate_data_to_command(data)
        if command[0] == "JOIN":
            command_join(client_socket, command)
            break
        else:
            client_socket.send("You have to join a channel first\n".encode())


def send_user_to_lobby(client_socket):
    while True:
        data = get_data(client_socket)
        command = translate_data_to_command(data)
        perform_command(client_socket,command)


###QUIT EXISTERAR INTE FÖR TILLFÄLLET###
def client_func(client_socket, addr):
    users[client_socket] = user.UserConfig(None, client_socket, addr)
    print("Connected By " + str(addr))
    request_nickname(client_socket)
    request_channel_join(client_socket) # welcome the user by adding into a channel
    send_user_to_lobby(client_socket)


# acceptera inkommande anslutningar, hantera dem i en separat tråd
while True:
    client_sock, addr = s.accept()
    t = threading.Thread(
        target=client_func,
        args=(client_sock, addr))
    t.start()
s.close()
