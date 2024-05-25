import threading
import socket
import sys

host = '127.0.0.1'
port = 55569

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
nickname_to_client = {}
server_running = True

def broadcast(message):
    for client in clients:
        client.send(message)
    
def broadcast_active_users():
    online_users = ", ".join(nicknames)
    broadcast(f"Online users: {online_users}\n".encode("utf-8"))

def broadcast_active_users_to_all():
    online_users = ", ".join(nicknames)
    active_users_message = f"Online users: {online_users}\n"
    for client in clients:
        client.send(active_users_message.encode("utf-8"))

def handle(client):
    if len(nicknames) > 1:
        send_active_users(client)
        #broadcast_active_users()  # Broadcast updated active users list

    while server_running:
        try:
            message = client.recv(1024).decode("utf-8")
            if message.startswith('/pm'):
                recipient, msg = message.split(' ', 2)[1:]  # Extract recipient and message
                recipient = recipient.strip()
                recipient_client = nickname_to_client.get(recipient)
                sender_nickname = nicknames[clients.index(client)]
                if recipient_client:
                    # Send the message to the recipient
                    recipient_client.send(f"[PM from {sender_nickname}]: {msg}".encode('utf-8'))
                    # Send a copy of the message to the sender
                    client.send(f"[PM to {recipient}]: {msg}".encode('utf-8'))
                else:
                    client.send(f"User {recipient} is not online or does not exist.".encode('utf-8'))
            elif message == '/active_users':
                broadcast_active_users()
            else:
                broadcast(f"{nicknames[clients.index(client)]}: {message}".encode('utf-8'))
        except:
            # Handle client disconnection
            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} left the chat.".encode('utf-8'))
            client.close()
            del nickname_to_client[nickname]
            break

        
def send_active_users(client):
    if len(nicknames) > 1:
        online_users = ", ".join(nicknames[:-1])  # Exclude the last joined user
        client.send(f"Online users: {online_users}\n".encode("utf-8"))

def receive():
    global server_running
    while server_running:
        try:
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            client.send("NICK".encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
        
            nicknames.append(nickname)
            clients.append(client)
            nickname_to_client[nickname] = client

            if len(clients) > 1:
                send_active_users(client)

            if len(clients) == 1:  # If the first user, send a welcome message
                client.send("Connected to the server!\n".encode("utf-8"))
            else:
                broadcast(f"{nickname} joined the chat!\n".encode("utf-8"))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")

# Define the function to stop the server
def stop_server():
    global server_running
    print("Stopping server...")
    server_running = False
    try:
        # Close the server socket
        server.close()
    except Exception as e:
        print(f"Error while stopping server: {e}")
    keyboard.unhook_all()
    sys.exit(0)  # Exit the program

print("SERVER IS ACTIVE...")
receive()
