# War_Game
Homework 3 for CS520 UW Milwaukee

## Problem Statement:

## Homework 3: implementing a stateful network protocol

This assignment will require you to write an implementation of a server for a very simple stateful network protocol. You will implement both the server and the client, and they will be expected both to speak the protocol correctly to each other.

#### WAR: A Card game

Hearthstone: Heroes of Warcraft is a cross-platform online card game with “war” in the title. No matter whether using a Mac, PC, iOS, or Android device, anyone can play the game with anyone else. The original card game [war](https://en.wikipedia.org/wiki/War_(card_game)), however, is much simpler than that game (although probably not more popular). For this assignment, we will be programming a cross-platform implementation of the “war” card game server. If you implement the protocol correctly, your code will be able to communicate with any other student’s code regardless of the choice of language.

#### WAR: The simplified rules

The simplified rules for our version of war are as follows: the dealer (server) deals half of the deck, at random, to the two players (clients). Each player “turns over” (sends) one of their cards to the server, and the server responds to each player “win” “lose” or “draw.” Unlike normal war (as this class is about network programming not video game programming), in the event of a tie neither player receives a “point” and play simply moves on to the next round. After all of the cards have been used, play stops and each client knows (based on the number of points they received) whether they won or they lost. Once each player has received the results of 26 rounds, they disconnect.

#### WAR: The message format

All WAR game messages follow the WAR message format. Each type of message has a fixed size, but not all messages are the same size. Each message consists of a one byte “command” followed by either a one byte payload or a 26 byte payload. The command values map as such:

 

COMMAND        VALUE
-------------------------------  
want game              0
game start               1
play card                  2
play result                3

For want game, play card, and play result, the payload is one byte long. For the “want game” message, the “result” should always be the value 0.

For the “game start” message (where the payload is a set of 26 cards), the payload is 26 bytes representing 26 cards. The byte representation of cards are a mapping between each of the 52 cards in a standard deck to the integers [0..51]. Mapping cards follows the suit order clubs, diamonds, hearts, spades, and within each suit, the rank order by value (i.e. 2, 3, 4, … , 10, Jack, Queen, King, Ace). Thus, 0, 1, and 2 map onto 2 of Clubs, 3 of Clubs, 4 of Clubs; 11, 12, 13, and 14 map onto the King of Clubs, the Ace of Clubs, the 2 of Diamonds, and the 3 of Diamonds; and finally 49, 50, and 51 map onto the Queen, King, and Ace of Spades. In this game, clubs is the weakest set of cards, and spades is the strongest. Note that you cannot compare card values directly to determine the winner of a “war” - you’ll need to write a custom comparison function which maps two different card values onto win, lose, or draw.

When sending a “game start” message, the server sends half of the deck, at random, to each player by sending 26 bytes with the values [0..51] to one player and the remaining 26 to the other player.

When sending a “play card” message, the client sends one byte which represents one of their cards. Which card to send is undefined, but you cannot send the same card twice within the same game.

Within a “play result” message, the one byte payload values map as such:


RESULT        VALUE
---------------------
win                   0
draw                1
lose                  2

#### WAR: the network protocol

Parallel to the simplified rules, the WAR protocol is as follows. A war server listens for new TCP connections on a given port. For this assignment, we use port 4444 for simplicity. Therefore, you run your server like this:

python war-server.py 4444

4444 is the port that your server should listen on.

The server waits until two clients are connected to that port. Therefore, you run each of your clients like this:

python war-client.py 127.0.0.1 4444

You might ask what is 127.0.0.1? This is the IP address of your local machine (e.g., your laptop). Basically, you are asking the client to connect to a server that is running on your LOCAL MACHINE, and listens to port 4444. 

Once both clients are connected, the clients send a message containing the “want game” command. If both clients do this correctly, the server responds with a message containing the “game start” command, with a payload containing the list of cards dealt to that client.

After each client has received their half of the deck, the clients send messages including the “play card” message, and set the payload to their chosen card. After the server has received a “play card” message from both clients, it will respond with a “play result” message to both clients, telling each one whether they won or lost. This process continues until each player has sent all of their cards and received all of their play results; after receiving the last play result, the clients disconnect; after sending the last play result, the server also disconnects. 

Please note that the war-client.py should NOT get the commands (want game, etc.) from the stdin. In the other words, you are not supposed to enter this commands and hit enter. Your client code should connect to the server automatically and send the above-mentioned commands automatically. 


For War v.1, your server and client only need to play one game, and then exit.

#### pcap file

The provided `example_play.pcap` shows the correct run of a single full game played with a correctly functioning server. You need to open this file with wireshark. Once you opened it, you will need to open Application layer header to see the payload that is getting transferred between client and server. 

 

#### Grading


All games should complete in well under **one second**. Any games taking more than one second to complete will be treated as broken / non-functioning.

 

TASK                                                                                      POINTS
-----------------------------------------------------------------------------------------------------
Successfully run a game of war between two correctly functioning clients                    7
Successfully handle an incorrect functioning client, with one game running                  3

For the incorrect functioning client, we test your server with a client that picks a value more than 26 (or less than 0) to see how your server handles this situation. A normal server would break the game without crashing. You don't need to submit the buggy client but make sure that you test your server against a buggy client (VERY slight change to your working client). 


This assignment will be graded out of 10 points, and is worth as much as every other homework assignment.

 

#### Due date and submission guidelines:


You need to submit two files: war-server.py and war-client.py. 
This assignment is due **Wednesday, October 26th at 11:59 pm**. Please get started early.