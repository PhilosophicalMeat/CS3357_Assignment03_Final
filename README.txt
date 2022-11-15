TO LAUNCH SERVER WITH NO ADJACENT ROOMS:
python room.py <serverport> <servername> <description> <item01> <item02> ... <itemn>
Example:
python room.py 7777 Cellar "An old cellar." "bottle" "rag" "torch"
- Server Port: 7777
- Server Name: "Cellar"
- Server Description: "An old cellar."
- Items currently in room:
"bottle"
"rag"
"torch"


TO LAUNCH SERVER WITH ADJACENT ROOMS:
- Notes on setup: adjacent servers must be launched in a separate window in order
for a client to access said room
- Same basic setup for line above, but add the following anywhere either before or
after (NOT in between) the required elements:
<directionindicator> room://<hostname>:<portnumber>
For example:
-s room://localhost:7777
establishes a connection to an adjacent room to the south




TO LAUNCH CLIENT:
python player.py <playername> room://<hostname>:<portnumber>
Example:
python player.py bob room://localhost:7777
Connects the player named "bob" to the room tied to localhost at port 7777




PLAYER COMMANDS (on lines beginning with '>'):
> look
- Prints a description of the room the player is currently in

> inventory
- Prints a list of the items the player is currently holding. Tells player they 
are holding nothing if inventory is empty

> take <item>
- Take an item from the room at add it to player's inventory. Informs player if the
requested item is not in the room. Invalid if the player does not add an item as a
parameter.

> drop <item>
- Drop a specified item from the player's inventory and adds it to the room's list of
allotted items. Informs player if they are not currently holding the specified item.
Ivalid if player does not add an item as a parameter.

> say <message>
- Player says something to the other occupants of the server. Invalid if the player does
not add a message as a parameter.

> exit
- Player drops all items currently in their inventory, disconnects from the server, and
closes the application. Other players in the server are informed of the player's 
departure. 

> CTRL + C
- Keyboard command equivalent to calling the 'exit' command. Also works to forcefully
shut down a server.

COMMANDS FOR ROOM TRAVERSAL:
> <directionindicator>
- player will attempt to enter connected server in the specified direction. 

Available directions include:
> north
> south
> east
> west
> up
> down
- Other players will be informed of player's departure, as well as the direction in which 
they departed. Players in the adjacent room will be notified of the player's arrival. 
Invalid if there is no adjacent room in the specified direction.