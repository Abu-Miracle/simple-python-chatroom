import socket
import threading

host = '127.0.0.1'
port = 55569

class Client:
    
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.nickname = input("PLEASE CHOOSE A NICKNAME: ")

        self.running = True

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.send_messages()
    
    def send_messages(self):
        while self.running:
            message = input("Enter Message: ")
            if message.startswith('/pm'):
                self.sock.send(message.encode("utf-8"))  # Send private message command
            else:
                self.sock.send(message.encode("utf-8"))  # Send as public message

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode("utf-8")
                if message == 'NICK':
                    self.sock.send(self.nickname.encode("utf-8"))
                else:
                    print(message)
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break
    
    def stop(self):
        self.running = False
        self.sock.close()
        exit(0)

client = Client(host, port)
