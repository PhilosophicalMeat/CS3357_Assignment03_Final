# CS3357 Assignment 03
# Room/ Server file
# Author: Ethan Christie (echris22)
# Student ID: 251177920
# Date: November 3, 2022
# Python file that represents the server/ room that players enter/ interact with.

import socket
import signal
import sys
import argparse
from urllib.parse import urlparse

# Saved information on the room.
connections = []
name = ''
description = ''
items = []
room_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Constant list used for checking if a movement command was called
DIRECTIONS = ['NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN']
# List of clients currently in the room.

client_list = []


# Signal handler for graceful exiting.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)


# Confirm that movement to another room is possible

def server_get_room(direction):
    global connections
    global DIRECTIONS

    for adjacent_server in connections:
        if adjacent_server[0].upper() == direction.upper():
            return '{} {} {}'.format(adjacent_server[0], adjacent_server[1], adjacent_server[2])
        else:
            if direction.upper() != "UP" and direction.upper() != "DOWN":
                return 'There is no hatch leading {}.'.format(direction)
            else:
                return 'There is no door to the {}.'.format(direction)


# Search the client list for a particular player.

def client_search(player):
    for reg in client_list:
        if reg[0] == player:
            return reg[1]
    return None


# Search the client list for a particular player by their address.

def client_search_by_address(address):
    for reg in client_list:
        if reg[1] == address:
            return reg[0]
    return None


# Add a player to the client list.

def client_add(player, address):
    registration = (player, address)
    client_list.append(registration)


# Remove a client when disconnected.

def client_remove(player):
    for reg in client_list:
        if reg[0] == player:
            client_list.remove(reg)
            break


# Summarize the room into text.

def summarize_room():
    global name
    global description
    global items
    global connections
    global client_list

    # Putting room name and description into a string
    summary = name + '\n\n' + description + '\n'

    # Loop for adding available connections
    for room in connections:
        if room[0] != "":
            # For rooms going in cardinal directions
            if room[0] != "up" or room[0] != "down":
                summary += 'A doorway leads away from the room to the ' + room[0] + '.\n'
            # For rooms going up/ down
            else:
                summary += 'A hatch leads out of the room going ' + room[0] + '.\n'
    summary += '\n'

    # Adding room's items to summary
    if len(items) == 0:
        summary += "The room is empty.\n"
    elif len(items) == 1:
        summary += "In this room, there is:\n"
        summary += f'  {items[0]}\n'
    else:
        summary += "In this room, there are:\n"
        for item in items:
            summary += f'  {item}\n'

    # Returning the completed summary
    return summary


# Print a room's description.

def print_room_summary():
    print(summarize_room()[:-1])


# Function for sending message to players
def send_message(message, sender_addr):
    # Search for sender to get name
    sender_name = client_search_by_address(sender_addr)
    server_message = '{} said \"{}\"'.format(sender_name, message)
    server_alert(server_message, sender_addr)


# Function for sending messages to rest of server members
def server_alert(server_message, addr):
    # Print message to server so long as it is not a join message (meant for other players specifically)
    if not server_message.__contains__('entered'):
        print(server_message)
    # Sending alert message to remaining players in the server
    for client in client_list:
        if client[1] != addr:
            room_socket.sendto(server_message.encode(), client[1])


# Function for checking if there is a room in the requested direction
def get_room_details(direction, addr):
    # Get client name for server-wide message
    client_name = client_search_by_address(addr)
    server_msg = '{} has left the room, heading {}.'.format(client_name, direction)
    return_msg = 'There is no room to the {}.'.format(direction)
    does_exist = False
    # Loop for checking available connections
    for room in connections:
        # If the current room's direction matches the desired direction of travel, add the rooms values to the return message
        if room[0] == direction:
            return_msg = '{} {} {}'.format(room[0], room[1], room[2])
            does_exist = True
    # If there is a room connected in the desired direction, send a server alert that the player has left in that direction
    if does_exist:
        server_alert(server_msg, addr)
    return return_msg


# Process incoming message.

def process_message(message, addr):
    # Parse the message.

    words = message.split()

    # If player is joining the server, add them to the list of players.

    if (words[0] == 'join'):
        if (len(words) == 2):
            client_add(words[1], addr)
            print(f'User {words[1]} joined from address {addr}')
            server_message = '{} has entered the room'.format(words[1])
            server_alert(server_message, addr)
            return summarize_room()[:-1]
        else:
            return "Invalid command"

    # If player is leaving the server. remove them from the list of players.

    elif (message == 'exit'):
        server_message = '{} has left the room.'.format(client_search_by_address(addr))
        client_remove(client_search_by_address(addr))
        server_alert(server_message, addr)
        return 'Goodbye'

    # If player looks around, give them the room summary.

    elif (message == 'look'):
        return summarize_room()[:-1]

    # If player takes an item, make sure it is here and give it to the player.

    elif (words[0] == 'take'):
        if (len(words) == 2):
            if (words[1] in items):
                items.remove(words[1])
                return f'{words[1]} taken'
            else:
                return f'{words[1]} cannot be taken in this room'
        else:
            return "Invalid command"

    # If player drops an item, put it in the list of things here.

    elif (words[0] == 'drop'):
        if (len(words) == 2):
            items.append(words[1])
            return f'{words[1]} dropped'
        else:
            return "Invalid command"

    # If a player says something, relay it to the rest of the players
    elif words[0] == 'say':
        sent_message = message.replace('say ', '')
        send_message(sent_message, addr)
        return 'You said \"{}\"'.format(sent_message)

    # If player tries to move to a another room, make sure there is a room in that direction, send either an error or
    # said rooms hostname and port number
    elif words[0].upper() in DIRECTIONS:
        response = get_room_details(words[0], addr)
        client_name = client_search_by_address(addr)
        client_remove((client_name, addr))
        return response

    # Otherwise, the command is bad.

    else:
        return "Invalid command"


# Our main function.

def main():
    global name
    global description
    global items
    global connections

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments for room settings.

    parser = argparse.ArgumentParser()
    # Parsing optional arguments for direction variables
    parser.add_argument("-s", type=str, nargs=1)
    parser.add_argument("-n", type=str, nargs=1)
    parser.add_argument("-e", type=str, nargs=1)
    parser.add_argument("-w", type=str, nargs=1)
    parser.add_argument("-u", type=str, nargs=1)
    parser.add_argument("-d", type=str, nargs=1)
    # Required arguments
    parser.add_argument("port", type=int, help="port number to list on")
    parser.add_argument("name", help="name of the room")
    parser.add_argument("description", help="description of the room")
    parser.add_argument("item", nargs='*', help="items found in the room by default")
    # Parsing arguments and assigning values to global variables
    args = parser.parse_args()

    port = args.port
    name = args.name
    description = args.description
    items = args.item
    # Updating connections list
    if args.n:
        server_addr = urlparse(args.n[0])
        connections.append(("north", str(server_addr.hostname), server_addr.port))
    if args.s:
        server_addr = urlparse(args.s[0])
        connections.append(("south", str(server_addr.hostname), server_addr.port))
    if args.e:
        server_addr = urlparse(args.e[0])
        connections.append(("east", str(server_addr.hostname), server_addr.port))
    if args.w:
        server_addr = urlparse(args.w[0])
        connections.append(("west", str(server_addr.hostname), server_addr.port))
    if args.u:
        server_addr = urlparse(args.u[0])
        connections.append(("up", str(server_addr.hostname), server_addr.port))
    if args.d:
        server_addr = urlparse(args.d[0])
        connections.append(("down", str(server_addr.hostname), server_addr.port))
    # Report initial room state.
    print('Room Starting Description:\n')
    print_room_summary()

    # Create the socket.  We will ask this to work on any interface and to use
    # the port given at the command line.  We'll print this out for clients to use.

    room_socket.bind(('', port))
    print('\nRoom will wait for players at port: ' + str(room_socket.getsockname()[1]))

    # Loop for sending and receiving messages from clients
    while True:
        # Receive a packet from a client and process it.

        message, addr = room_socket.recvfrom(1024)

        # Process the message and retrieve a response.

        response = process_message(message.decode(), addr)

        # Send the response message back to the client.

        room_socket.sendto(response.encode(), addr)


if __name__ == '__main__':
    main()
