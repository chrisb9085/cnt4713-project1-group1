import socket
import threading

import sys # Needed to read port numbers from command line

clients_lock = threading.Lock() # Mutex
clients = {} # username : (control_sock : data_sock)

HOST = "127.0.0.1"
PORT = int(sys.argv[1])


if PORT < 1024:
    print("Must input a port number greater than 1023.")
    sys.exit(0)

print("Starting server...")
print("Creating server socket")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Awaiting connections...")

def broadcast(message):
    with clients_lock:
        targets = [(u, i["data"]) for u, i in clients.items() if u != skip]

    for _, sock in targets:
        try:
            sock.sendall(message.encode())
        except:
            pass

def handle_conn():
    
    pass

def receive():
    while True:
        client, addr = server.accept()
        print("Connection requested. Creating data socket")

        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ds.bind((HOST, 0))
        ds.listen(1)
        data_port = ds.getsockname()[1]
        client.sendall(f"200\n\n{data_port}\n".encode())

        data, _ = ds.accept()
        ds.close()

        thread = threading.Thread(target=handle_conn, args=(None, client, data))
        thread.start()

receive()



# Commands:
# connect <ip> <port>
# login <username>
# who
# broadcast <msg> [done]
# private <username> <msg>
# quit

# Response format:
# Status Code
# <EMPTY LINE>
# Data section if required

