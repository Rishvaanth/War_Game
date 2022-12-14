import sys
import asyncio
import logging
from enum import Enum

if len(sys.argv) != 3:
    print(
        f"Correct usage: script, IP address of the game server, port number")  # Checking if port and IP addressess were input.
    exit()

HOST = str(sys.argv[1])
PORT = int(sys.argv[2])


class Command(Enum):
    WANTGAME = 0
    GAMESTART = 1
    PLAYCARD = 2
    PLAYRESULT = 3


class Result(Enum):
    WIN = 0
    DRAW = 1
    LOSE = 2


async def client(host, port, loop):
    try:

        reader, writer = await asyncio.open_connection(host, port, loop=loop)
        myscore = 0

        writer.write(b"\0\0")                       # want game
        card_msg = await reader.readexactly(27)     # expecting payload of the shuffled hand

        for card in card_msg[1:]:

            writer.write(bytes([Command.PLAYCARD.value, card]))     #play card
            result = await reader.readexactly(2)    #reading result

            if result[1] == Result.WIN.value:
                myscore += 1
            elif result[1] == Result.LOSE.value:
                myscore -= 1
        if myscore > 0:
            result = "won"
        elif myscore < 0:
            result = "lost"
        else:
            result = "drew"

        print(f"Game complete, you {result}!")
        writer.close()
        return 1
    except ConnectionResetError:
        logging.error("ConnectionResetError")
        return 0
    except asyncio.streams.IncompleteReadError:
        logging.error("asyncio.streams.IncompleteReadError")
        return 0
    except OSError:
        logging.error("OSError")
        return 0


loop = asyncio.get_event_loop()
loop.run_until_complete(client(HOST, PORT, loop))
