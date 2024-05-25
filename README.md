The setup process for this project is very easy
1.	First of all, create a new folder and name it accordingly. Open the folder using Visual Studio Code or any suitable text editor. 
2.	Then simply create two python files within the created folder, one for the server – ‘server.py’ and the other for the client – ‘client.py’

2.1 SETTING UP SERVER NODE
•	In the server file, you first need to import the necessary libraries that enables operations to be carried out.
    import threading
    import socket
•	Create a host variable that is assigned the IP address '127.0.0.1'. This IP address is known as the loopback address, which refers to the local machine itself. It basically facilitates connections to services running on the same machine. Create a port variable assigned to 55560. Ports are used to differentiate between different services running on the same machine. 
    host = '127.0.0.1'
    port = 55560
•	Create a new socket object called server using the socket.socket() method. It takes two parameters: socket.AF_INET specifies the address family (IPv4), and socket.SOCK_STREAM specifies the socket type (TCP). This creates a TCP socket. After this, bind the host and the port using the .bind() method and use the listen() function to activate the server and put it in a listening mode. 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
•	Create two empty lists to store information about connected clients and their username or ‘nickname’ and create an empty dictionary that will be used as a mapping between nicknames and client socket objects, allowing efficient lookup of clients by their nicknames.
    clients = []
    nicknames = []
    nickname_to_client = {}
•	Moving forward, we will create the broadcast function which facilitates communication between clients in the chatroom by ensuring that messages are broadcasted to all connected clients in a synchronous manner. It iterates over the list of client socket objects stored in the clients list and sends the provided message to each client individually.
    def broadcast(message):
        for client in clients:
            client.send(message)
•	We then create the handle function which serves as the core functionality for handling client connections on the server-side of the chatroom application. It acts as the intermediary between the server and individual clients, managing message reception, processing, broadcasting, and handling client connections and disconnections. It plays a central role in enabling communication within the chatroom application while ensuring proper handling of client interactions and messages. This function also facilitates private message handling between clients, ensuring privacy between  the sender and recipient.
    def handle(client):
        while True:
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
•	The receive function on the server side is typically responsible for accepting incoming connections from clients using the server.accept() method. It listens for and accepts new client connections, allowing multiple clients to connect to the server.
    def receive():
        while True:
            client, address = server.accept()
            print(f"Connected with {str(address)}")
    
            client.send("NICK".encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            
            nicknames.append(nickname)
            clients.append(client)
            nickname_to_client[nickname] = client
    
            print(f"Nickname of the client is {nickname}")
            broadcast(f"{nickname} joined the chat! \n".encode("utf-8"))
            client.send("Connected to the server!".encode("utf-8"))
    
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
•	Finally, we use a print a message to the client to show that the server is lstening and is ready to receive requests  

    print("SERVER IS ACTIVE...")
    receive()
2.2 SETTING UP CLIENT NODE
•	We first need to import the necessary libraries that will enable us to carry out operations on the client side. This also includes the libraries responsible for creatin the interface.
    import socket
    import threading
    import tkinter
    import tkinter.scrolledtext
    from tkinter import simpledialog
•	Create a host and a port variable with the same host IP address and port number as used in the server side.
    host = '127.0.0.1'
    port = 55560
•	We then create the client as a class because it has numerous advantages in terms of organization, structure, encapsulation, and potential for reuse and extension. Inside the client class contains the constructor which is used to initialize the client object and set up its initial state.
    class Client:
        def __init__(self, host, port):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
    
            msg = tkinter.Tk()
            msg.withdraw()
    
            self.nickname = simpledialog.askstring("Nickname", "PLEASE CHOOSE A NICKNAME", parent=msg)
    
            self.gui_done = False
            self.running = True
    
            gui_thread = threading.Thread(target=self.gui_loop)
            receive_thread = threading.Thread(target=self.receive)
    
            gui_thread.start()
            receive_thread.start()
•	We create the gui_loop function which is basically used to design the tkinter user interface for the chatroom. It provides options to adjust colour, padding, text area, input area, etc.
       def gui_loop(self):
              self.win = tkinter.Tk()
              self.win.configure(bg="cyan")
      
              self.chat_label = tkinter.Label(self.win, text="CHATROOM:", bg="cyan")
              self.chat_label.config(font=("Eras Bold ITC", 15))
              self.chat_label.pack(padx=20, pady=5)
      
              self.text_area = tkinter.scrolledtext.ScrolledText(self.win, bg="lightgray")
              self.text_area.pack(padx=10, pady=3)
              self.text_area.config(state="disabled", font=("MS Sans Serif", 12), height=10)
      
              self.msg_label = tkinter.Label(self.win, text="Enter Message Here:", bg="cyan")
              self.msg_label.config(font=("MS Sans Serif", 14))
              self.msg_label.pack(padx=20, pady=5)
      
              self.input_area = tkinter.Text(self.win, height=2, bg="lightgray")
              self.input_area.config(font=("MS Sans Serif", 12))
              self.input_area.pack(padx=10, pady=5)
      
              self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
              self.send_button.config(font=("MS Sans Serif", 12))
              self.send_button.pack(padx=20, pady=5)
      
              self.gui_done = True
      
              self.win.protocol("WM_DELETE_WINDOW", self.stop)
      
              self.win.mainloop()

SCREENSHOTS
![Screenshot (122)](https://github.com/Abu-Miracle/simple-python-chatroom/assets/136976924/d1a6f699-d95d-4b52-8855-64d3ab256c8d)
![Screenshot (121)](https://github.com/Abu-Miracle/simple-python-chatroom/assets/136976924/3bedacdb-eba3-4a50-9106-f0cdf74ce3a5)
![Screenshot (120)](https://github.com/Abu-Miracle/simple-python-chatroom/assets/136976924/592ac95a-67c4-4fa0-bb3b-d8f27f7b852a)
![Screenshot (119)](https://github.com/Abu-Miracle/simple-python-chatroom/assets/136976924/dcf09366-a91b-4b84-b3ba-54b14ead9c9f)
![Screenshot (118)](https://github.com/Abu-Miracle/simple-python-chatroom/assets/136976924/895590eb-4223-4f5d-b7a9-b8ab8ae07e11)
![Screenshot (123)](https://github.com/Abu-Miracle/simple-python-chatroom/assets/136976924/840db256-b08a-4799-a472-cbb9ef62e1ef)
