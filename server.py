import socket
import threading

import sys # Needed to read port numbers from command line

clients_lock = threading.Lock() # Mutex
clients = {} # client : username

HOST = "127.0.0.1"
PORT = int(sys.argv[1])


if PORT < 1024:
    print("Must input a port number greater than 1023.")
    exit(0)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

def broadcast(message):
    for client in clients.keys:
        client.send(message)

def handle_conn(client):
    while True:
        try:
            message = client.recv(1024) # 1 kb of data
            broadcast(message)
        except:
            clients.pop(client)

# Commands:
# connect <ip> <port>
# login <username>
# who
# broadcast <msg>
# private <username> <msg>
# quit

# Response format:
# Status Code
# <EMPTY LINE>
# Data section if required

