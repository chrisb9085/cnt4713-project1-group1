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
        targets = [(u, i["data"]) for u, i in clients.items()]

    for _, sock in targets:
        try:
            sock.sendall(message.encode())
        except:
            pass

def handle_login(args, ctrl, data):
    with clients_lock:
        if args in clients:
            data.sendall("500\n\nUsername taken\n".encode())
            return None
        clients[args] = {"control": ctrl, "data": data}
    print(f"Login requested by: {args}")
    broadcast(f"200\n\njoin\n{args}\n")
    return args

def handle_who(data):
    print("Who requested. Sending users.")
    with clients_lock:
        ul = ", ".join(clients.keys())
    data.sendall(f"200\n\n{ul}\n".encode())

def handle_broadcast(user, args):
    print(f"Broadcast requested by {user}\nMessage: {args}")
    broadcast(f"200\n\nBroadcast\n{user}\n{args}\n")

def handle_private(user, args, data):
    p = args.split(" ", 1)
    if len(p) < 2:
        data.sendall("500\n\nUsage: private <user> <msg>\n".encode())
        return
    recip, msg = p
    with clients_lock:
        target = clients.get(recip)
    if not target:
        data.sendall("500\n\nUser not found\n".encode())
        return
    print(f"Private message from {user} to {recip}")
    target["data"].sendall(f"200\n\nPrivate\n{user}\n{msg}\n".encode())
    data.sendall("200\n\n".encode())

def handle_quit(user, data):
    print(f"Quit requested by {user}")
    with clients_lock:
        clients.pop(user, None)
    broadcast(f"200\n\nquit\n{user}\n")
    data.sendall("200\n\n".encode())

def handle_conn(user, ctrl, data):
    try:
        for raw in ctrl.makefile("r"): # Tokenizes input
            parts = raw.strip().split(" ", 1)
            cmd = parts[0].lower()
            args = parts[1]
        
            if cmd == "login":
                user = handle_login(args, ctrl, data)
            elif cmd == "who":
                handle_who(data)
            elif cmd == "broadcast":
                handle_broadcast(user,args)
            elif cmd == "private":
                handle_private(user, args, data)
            elif cmd == "quit":
                handle_quit(user, data)
                break
    except:
        pass
    finally:
        if user:
            with clients_lock:
                clients.pop(user, None)
            broadcast(f"200\n\nquit\n{user}\n")
        for s in (data, ctrl):
            try:
                s.close()
            except:
                pass

def receive():
    while True:
        client, _ = server.accept()
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

