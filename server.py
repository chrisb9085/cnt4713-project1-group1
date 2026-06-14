import socket
import threading

import sys # Needed to read port numbers from command line

clients_lock = threading.Lock() # Mutex
clients = {} # username : (control_sock : data_sock)

PORT = int(sys.argv[1]) # Read port from cmd line



print("Starting server...")
print("Creating server socket")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP socket
server.bind(("", PORT)) # Bind to all interfaces on given port
server.listen() # Start listening for connections
print("Awaiting connections...")

def broadcast(message):
    with clients_lock: # Lock before reading clients (prevents race condition)
        targets = [(u, i["data"]) for u, i in clients.items()] # all data sockets

    for _, sock in targets:
        try:
            sock.sendall(message.encode()) # Send to each client's data socket
        except:
            pass

def handle_login(args, ctrl, data):
    with clients_lock:
        if args in clients:
            data.sendall("500\n\nUsername taken\n".encode()) # 500 status code is duplicate username is found
            return None
        clients[args] = {"control": ctrl, "data": data} # Add user to dict
    print(f"Login requested by: {args}")
    broadcast(f"200\n\njoin\n{args}\n") # Notifies clients of new user
    return args

def handle_who(data):
    print("Who requested. Sending users.")
    with clients_lock:
        ul = ", ".join(clients.keys()) # lists usernames separated by a comma
    data.sendall(f"200\n\n{ul}\n".encode())

def handle_broadcast(user, args):
    print(f"Broadcast requested by {user}\nMessage: {args}")
    broadcast(f"200\n\nBroadcast\n{user}\n{args}\n")

def handle_private(user, args, data):
    p = args.split(" ", 1) # Splits into recipient and message
    
    recip, msg = p
    with clients_lock: # Thread Lock
        target = clients.get(recip) # lookup recipient
    if not target:
        data.sendall("500\n\nUser not found\n".encode())
        return
    print(f"Private message from {user} to {recip}")
    target["data"].sendall(f"200\n\nPrivate\n{user}\n{msg}\n".encode()) # Deliver msg to recipient
    data.sendall("200\n\n".encode()) # ACK to sender

def handle_quit(user, data):
    print(f"Quit requested by {user}")
    with clients_lock: # Thread lock
        clients.pop(user, None) # Removes user from dict
    broadcast(f"200\n\nquit\n{user}\n") # Broadcasts quitting msg to clients
    data.sendall("200\n\n".encode()) # ACK to user

def handle_conn(user, ctrl, data):
    try:
        for raw in ctrl.makefile("r"): # Tokenizing input
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
                user = None
                break
    except:
        pass
    finally:
        if user:
            with clients_lock:
                clients.pop(user, None)
            broadcast(f"200\n\nquit\n{user}\n")
        for s in (data, ctrl): # Close sockets
            try:
                s.close()
            except:
                pass

def receive():
    while True:
        client, _ = server.accept() # Wait for new conn
        print("Connection requested. Creating data socket")

        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ds.bind(("", 0)) # Port 0 lets OS pick free port
        ds.listen(1)
        data_port = ds.getsockname()[1]
        client.sendall(f"200\n\n{data_port}\n".encode()) # Tell client which port to use

        data, _ = ds.accept() # Accept client's data conn
        ds.close() # Closes listening socket once connection is established

        # Creates a new thread for client
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

