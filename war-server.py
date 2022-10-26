import sys
import socket
import asyncio
import logging
import random
import select
import threading
from enum import Enum

if len(sys.argv) != 2:  # Checking if Port is entered as an argument.
    print(f"Correct usage: script, port number")
    exit()

endGame = False


class Command(Enum):
    WANTGAME = 0
    GAMESTART = 1
    PLAYCARD = 2
    PLAYRESULT = 3


HOST = '127.0.0.1'
PORT = int(sys.argv[1])
matchMakingClients = list()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind((HOST, PORT))


def startServer():
    loop = asyncio.get_event_loop()
    co_routine = asyncio.start_server(pair_clients, HOST, PORT, loop=loop)

    server = loop.run_until_complete(co_routine)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except endGame:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())

    loop.close()


async def pair_clients(reader, writer):
    for clients in matchMakingClients:
        if clients[1] is None:
            clients[1] = (reader, writer)
            await handle_game(clients[0], clients[1])
            clients[0][1].close()
            clients[1][1].close()
            matchMakingClients.remove(clients)
            return

    matchMakingClients.append([(reader, writer), None])


async def handle_game(player1, player2):
    split_deck = shuffleDeck()
    c1_cards = split_deck[0]
    c2_cards = split_deck[1]

    c1_used = [False] * 26
    c2_used = [False] * 26

    try:
        f_client_data = await player1[0].readexactly(2)
        s_client_data = await player2[0].readexactly(2)

        if (f_client_data[1] != 0) or s_client_data[1] != 0:
            print('ERROR... User does not enter in 0 for the first time')
            kill_game(player1[1], player2[1])
            kill_game(player1[1].get_extra_info('socket'),
                      player2[1].get_extra_info('socket'))
            return

        # Clients are ready for their cards
        player1[1].write(bytes(([Command.GAMESTART.value] + c1_cards)))
        player2[1].write(bytes(([Command.GAMESTART.value] + c2_cards)))

        total_turns = 0

        while total_turns < 26:

            f_client_data = await player1[0].readexactly(2)
            s_client_data = await player2[0].readexactly(2)

            # Check if first byte was 'play card'
            if f_client_data[0] != 2 and s_client_data[0] != 2:
                print('Error... User does not enter in 2.')
                kill_game(player1[1], player2[1])
                kill_game(player1[1].get_extra_info('socket'),
                          player2[1].get_extra_info('socket'))
                return

            # Check if card is in deck

            if check_card(f_client_data[1], split_deck[0]) is False \
                    or check_card(s_client_data[1], split_deck[1]) is False:
                print('Error... A clients card does not match card dealt')
                kill_game(player1[1], player2[1])
                kill_game(player1[1].get_extra_info('socket'),
                          player2[1].get_extra_info('socket'))
                return

            # Check if card was already used
            for x in range(0, 26):

                if f_client_data[1] == c1_cards[x] or \
                        s_client_data[1] == c2_cards[x]:

                    if f_client_data[1] == c1_cards[x]:

                        if c1_used[x] is False:
                            c1_used[x] = True
                        else:
                            print('Error: A client tried to use '
                                  'the same card again ')
                            kill_game(player1[1], player2[1])
                            kill_game(player1[1].get_extra_info('socket'),
                                      player2[1].get_extra_info('socket'))
                            return

                    if s_client_data[1] == c2_cards[x]:
                        if c2_used[x] is False:
                            c2_used[x] = True
                        else:
                            print('Error: A client tried to use '
                                  'the same card again ')
                            kill_game(player1[1], player2[1])
                            kill_game(player1[1].get_extra_info('socket'),
                                      player2[1].get_extra_info('socket'))
                            return

            # Get the results for the first and second client
            c1_result = compare_cards(f_client_data[1], s_client_data[1])
            c2_result = compare_cards(s_client_data[1], f_client_data[1])

            # Concat the command to send with the result
            c1_send_result = [Command.PLAYRESULT.value, c1_result]
            c2_send_result = [Command.PLAYRESULT.value, c2_result]

            # Write back to the client
            player1[1].write(bytes(c1_send_result))
            player2[1].write(bytes(c2_send_result))

            total_turns += 1

        # Close the connections
        kill_game(player1[1], player2[1])
        kill_game(player1[1].get_extra_info('socket'),
                  player2[1].get_extra_info('socket'))
        global endGame
        endGame = True

    except ConnectionResetError:
        logging.error("ConnectionResetError")
        return 0
    except asyncio.streams.IncompleteReadError:
        logging.error("asyncio.streams.IncompleteReadError")
        return 0
    except OSError:
        logging.error("OSError")
        return 0


def shuffleDeck():
    deck_size = 52
    deck = [index for index in range(deck_size)]
    random.shuffle(deck)
    first_hand = []
    second_hand = []

    # Probably more efficient ways of doing this (slicing)
    while len(deck) > 0:
        dealt_card = deck.pop()
        if len(first_hand) < 26:
            first_hand.append(dealt_card)
        else:
            second_hand.append(dealt_card)

    both_hands = [first_hand, second_hand]
    return both_hands


def kill_game(s1, s2):
    s1.close()
    s2.close()
    pass


def check_card(card, deck):
    if card not in deck:
        return False
    return True


def compare_cards(card1, card2):
    first_card = card1 % 13
    second_card = card2 % 13

    # Return values changed here to match "RESULTS"
    if first_card < second_card:
        return 2
    elif first_card == second_card:
        return 1
    else:
        return 0


print(f"War game server started. \n Waiting for players to connect...")
startServer()
