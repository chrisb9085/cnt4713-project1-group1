import socket
import threading

control = None   # sends commands to server
data = None      # receives responses from server
running = True
last_command = ""  # tracks last command sent to distinguish bare 200 responses


def print_response(message):
    # Format server responses for user output
    lines = message.strip().split("\n")

    if len(lines) == 0:
        return

    status = lines[0]

    if status == "200":

        if len(lines) == 1:
            if last_command.startswith("private"):
                print("200 status code received. Message sent.")
            else:
                print("200 status code received.")

        elif len(lines) >= 5 and lines[2] == "Broadcast":
            sender = lines[3]
            text = lines[4]

            print("200 status code received.")
            print("Broadcast message from " + sender + ": " + text)

        elif len(lines) >= 5 and lines[2] == "Private":
            sender = lines[3]
            text = lines[4]

            print("200 status code received.")
            print(sender + ": " + text)

        elif len(lines) >= 4 and lines[2] == "join":
            print("200 status code received. Login successful")

        elif len(lines) >= 4 and lines[2] == "quit":
            print("200 status code received.")

        elif len(lines) >= 3:
            print("200 status code received. Users currently connected: " + lines[2])

        else:
            print("200 status code received.")

    elif status == "500":
        print("500 status code received.")

        if len(lines) >= 3:
            print(lines[2])


def receive_messages():
    # Background thread for incoming server messages
    global running

    while running:
        try:
            message = data.recv(1024).decode()

            if not message:
                break

            print_response(message)

        except:
            break


def connect_to_server(command):
    # Create control connection, get data port, then create data connection
    global control, data

    parts = command.split()

    if len(parts) != 3:
        print("Invalid connect command.")
        return False

    ip = parts[1]
    port = int(parts[2])

    control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control.connect((ip, port))

    response = control.recv(1024).decode()
    lines = response.strip().split("\n")

    if lines[0] != "200":
        print("500 status code received.")
        return False

    data_port = int(lines[2])

    print("200 status code received. Starting data connection on port " + str(data_port))

    data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data.connect((ip, data_port))

    thread = threading.Thread(target=receive_messages)
    thread.daemon = True
    thread.start()

    return True


def main():
    # Read user commands and send them to server
    global running, last_command

    print("Starting client...")

    connected = False

    while running:
        command = input("> ")

        if command.startswith("connect"):
            connected = connect_to_server(command)

        elif not connected:
            print("You must connect first.")

        else:
            try:
                last_command = command
                control.sendall((command + "\n").encode())

                if command == "quit":
                    running = False
                    break

            except:
                print("Error sending command.")
                running = False
                break

    try:
        control.close()
        data.close()
    except:
        pass


main()
