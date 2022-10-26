import socket

HOST = '127.0.0.1'
PORT = 4444

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
    clientsocket.connect((HOST, PORT))
    clientsocket.sendall(b"Hello, world")
    data = clientsocket.recv(1024)


print(f"Received {data!r}")
