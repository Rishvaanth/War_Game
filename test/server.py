import socket
import sys
import selectors
import types

HOST = '127.0.0.1'
PORT = 4444

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    connection, address = s.accept()

    with connection:
        print(f"Connected by {address}")
        print(f"Connection is: {connection}")
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(data)