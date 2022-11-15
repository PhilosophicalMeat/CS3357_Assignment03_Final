# CS3357 Assignment 03
# Player/ Client file
# Author: Ethan Christie (echris22)
# Student ID: 251177920
# Date: November 3, 2022
# Python file used by player/ client to interact with server

import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Constant list used for checking if a movement command was called
DIRECTIONS = ['NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN']
# Creating client selector
client_selector = selectors.DefaultSelector()

# Server address.

server = ('', '')

# User name for player.

name = ''

# Inventory of items.

inventory = []


# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    for item in inventory:
        message = f'drop {item}'
        client_socket.sendto(message.encode(), server)
    message = 'exit'
    client_socket.sendto(message.encode(), server)
    sys.exit(0)


# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)


# Function to join a room.

def join_room():
    message = f'join {name}'
    client_socket.sendto(message.encode(), server)
    response, addr = client_socket.recvfrom(1024)
    print(response.decode())


# Function for handling socket data
def handle_socket_data(sock, mask):
    global server
    message, addr = sock.recvfrom(1024)
    message = message.decode()
    words = message.split()

    # Response to 'take' command
    if ((len(words) == 2) and (words[1] == 'taken')):
        inventory.append(words[0])
        print(message)
    # Response to 'drop' command
    elif len(words) == 2 and words[1] == 'dropped':
        inventory.remove(words[0])
        print(message)
    # Response to move rooms command
    elif len(words) == 3 and words[0].upper() in DIRECTIONS:
        # Update server value
        server = (words[1], int(words[2]))
        join_room()
    else:
        print(message)


# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(file, mask):
    # get new line and Parse command.
    command = sys.stdin.readline()[:-1]
    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        client_socket.sendto(message.encode(), server)

    # Check for particular commands of interest from the user.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            client_socket.sendto(message.encode(), server)
        sys.exit(0)
    # elif (command == 'look'):
    #     response, addr = client_socket.recvfrom(1024)
    #     print(response.decode())
    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')
    # elif (words[0] == 'take'):
    #     response, addr = client_socket.recvfrom(1024)
    #     print(response.decode())
    #     words = response.decode().split()
    #     if ((len(words) == 2) and (words[1] == 'taken')):
    #         inventory.append(words[0])
    # elif (words[0] == 'drop'):
    #     response, addr = client_socket.recvfrom(1024)
    #     print(response.decode())
    #     inventory.remove(words[1])
    # else:
    #     response, addr = client_socket.recvfrom(1024)
    #     print(response.decode())


# Our main function.

def main():
    global name
    global client_socket
    global server

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("server", help="URL indicating server location in form of room://host:port")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    try:
        server_address = urlparse(args.server)
        if ((server_address.scheme != 'room') or (server_address.port == None) or (server_address.hostname == None)):
            raise ValueError
        host = server_address.hostname
        port = server_address.port
        server = (host, port)
    except ValueError:
        print('Error:  Invalid server.  Enter a URL of the form:  room://host:port')
        sys.exit(1)
    name = args.name

    # Registering handlers for the client selector; one for receiving input from the client socket, the other for keyboard input
    client_selector.register(client_socket, selectors.EVENT_READ, handle_socket_data)
    client_selector.register(sys.stdin, selectors.EVENT_READ, process_command)
    # Send message to enter the room.

    join_room()

    # We now loop forever, sending commands to the server and reporting results

    while True:
        # Prompt the user before beginning.

        do_prompt()

        events = client_selector.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
        # # Get a line of input.
        #
        # line=sys.stdin.readline()[:-1]
        #
        # # Process command and send to the server.
        #
        # process_command(line)


if __name__ == '__main__':
    main()
