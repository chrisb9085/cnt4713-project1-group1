import socket
import threading

import sys # Needed to read port numbers from command line

clients_lock = threading.Lock() # Mutex
clients = {}

HOST = "127.0.0.1"
PORT = int(sys.argv[1])
PORT = "3400"

if PORT < 1024:
    print("Must input a port number greater than 1023.")
    exit(0)

def send_response(sock, status, lines=None):
    msg = str(status) + "\n\n"
    if lines:
        msg += "\n".join(str(l) for l in lines) + "\n"
    try:
        sock.sendall(msg.encode())
    except Exception:
        pass