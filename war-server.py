import sys
# import socket
import asyncio
import logging
import random
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


def startGameServer():
    loop = asyncio.get_event_loop()
    co_routine = asyncio.start_server(pair_clients, HOST, PORT, loop=loop)

    server = loop.run_until_complete(co_routine)

    gameServer = format(server.sockets[0].getsockname())
    print(f"Game server running on {gameServer}")
    print(f"Use Command+C or Ctrl+C to end the game server")
    try:
        loop.run_forever()
        print(endGame)
        if endGame:
            server.close()
            loop.run_until_complete(server.wait_closed())

            loop.close()

    except KeyboardInterrupt:
        pass
        server.close()
        loop.run_until_complete(server.wait_closed())

        loop.close()


async def pair_clients(reader, writer):
    for players in matchMakingClients:
        if players[1] is None:
            players[1] = (reader, writer)
            await handle_game(players[0], players[1])
            players[0][1].close()
            players[1][1].close()
            matchMakingClients.remove(players)
            return

    matchMakingClients.append([(reader, writer), None])


async def handle_game(player1, player2):
    split_deck = shuffleDeck()
    p1_deck = split_deck[0]
    p2_deck = split_deck[1]

    p1_used_cards = [False] * 26
    p2_used_cards = [False] * 26

    try:
        p1_data = await player1[0].readexactly(2)
        p2_data = await player2[0].readexactly(2)

        if (p1_data[1] != 0) or p2_data[1] != 0:
            print('Invalid first command')
            kill_game(player1[1], player2[1])
            kill_game(player1[1].get_extra_info('socket'),
                      player2[1].get_extra_info('socket'))
            return

        player1[1].write(bytes(([Command.GAMESTART.value] + p1_deck)))     #Gamestart and issuing cards to the players
        player2[1].write(bytes(([Command.GAMESTART.value] + p2_deck)))

        total_turns = 0

        while total_turns < 26:

            p1_data = await player1[0].readexactly(2)
            p2_data = await player2[0].readexactly(2)

            if p1_data[0] != 2 and p2_data[0] != 2:  # Checking for playcard command
                print('Error... User does not enter in 2.')
                kill_game(player1[1], player2[1])
                kill_game(player1[1].get_extra_info('socket'),
                          player2[1].get_extra_info('socket'))
                return

            if check_card(p1_data[1], split_deck[0]) is False or check_card(p2_data[1],
                                                                            split_deck[1]) is False:          # Check if card is in deck
                print('Error... A clients card does not match card dealt')
                kill_game(player1[1], player2[1])
                kill_game(player1[1].get_extra_info('socket'),
                          player2[1].get_extra_info('socket'))
                return

            for card in range(0, 26):                                      # Checking for already pre used card

                if p1_data[1] == p1_deck[card] or p2_data[1] == p2_deck[card]:

                    if p1_data[1] == p1_deck[card]:

                        if p1_used_cards[card] is False:
                            p1_used_cards[card] = True
                        else:
                            print('Error: A client tried to use '
                                  'the same card again ')
                            kill_game(player1[1], player2[1])
                            kill_game(player1[1].get_extra_info('socket'),
                                      player2[1].get_extra_info('socket'))
                            return

                    if p2_data[1] == p2_deck[card]:
                        if p2_used_cards[card] is False:
                            p2_used_cards[card] = True
                        else:
                            print('Error: A client tried to use '
                                  'the same card again ')
                            kill_game(player1[1], player2[1])
                            kill_game(player1[1].get_extra_info('socket'),
                                      player2[1].get_extra_info('socket'))
                            return

            c1_result = compare_cards(p1_data[1], p2_data[1])
            c2_result = compare_cards(p2_data[1], p1_data[1])

            c1_send_result = [Command.PLAYRESULT.value, c1_result]
            c2_send_result = [Command.PLAYRESULT.value, c2_result]

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
    numberOfCards = 52
    deck = [index for index in range(numberOfCards)]
    random.shuffle(deck)
    first_hand = []
    second_hand = []

    # Probably more efficient ways of doing this (slicing)
    while len(deck) > 0:
        shuffledCard = deck.pop()
        if len(first_hand) < 26:
            first_hand.append(shuffledCard)
        else:
            second_hand.append(shuffledCard)

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

    if first_card < second_card:
        return 2
    elif first_card == second_card:
        return 1
    else:
        return 0


print(f"War game server started. \n Waiting for players to connect...")
startGameServer()
