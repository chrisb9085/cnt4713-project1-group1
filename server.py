import socket
import threading

import sys # Needed to read port numbers from command line

clients_lock = threading.Lock() # Mutex
clients = {}


def send_response(sock, status, lines=None):
    msg = str(status) + "\n\n"
    if lines:
        msg += "\n".join(str(l) for l in lines) + "\n"
    try:
        sock.sendall(msg.encode())
    except Exception:
        pass