import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import messagebox

host = '127.0.0.1'
port = 55569

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
    
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="cyan")

        self.chat_label = tkinter.Label(self.win, text="CHATROOM:\n", bg="cyan")
        self.chat_label.config(font=("Eras Bold ITC", 15))
        self.chat_label.pack(padx=20, pady=5)

        self.desc_label = tkinter.Label(self.win, text="Messages are sent to every user by default. \n To send a Private Message, Use the format: \n /pm [Recipient_name] [Message]", bg="cyan")
        self.desc_label.config(font=("MS Sans Serif", 13))
        self.desc_label.pack(padx=20, pady=3)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, bg="lightgray")
        self.text_area.pack(padx=10, pady=3)
        self.text_area.config(state="disabled", font=("MS Sans Serif", 12), height=10)

        self.msg_label = tkinter.Label(self.win, text="Enter Message Here:", bg="cyan")
        self.msg_label.config(font=("MS Sans Serif", 14))
        self.msg_label.pack(padx=20, pady=5)
 
        self.input_area = tkinter.Text(self.win, height=1, bg="lightgray")
        self.input_area.config(font=("MS Sans Serif", 12))
        self.input_area.pack(padx=10, pady=5)

        self.input_area.bind("<Return>", lambda event: self.write()) # Bind the <Return> event to the write method

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("MS Sans Serif", 12))
        self.send_button.pack(padx=20, pady=5)

        self.active_users_button = tkinter.Button(self.win, text="See Active Users", command=self.get_active_users)
        self.active_users_button.config(font=("MS Sans Serif", 12))
        self.active_users_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()
    
    def write(self):
        message = self.input_area.get('1.0', 'end').strip()
        if message.startswith('/pm'):
            recipient, msg = message.split(' ', 2)[1:]  # Extract recipient and message
            self.sock.send(f"/pm {recipient} {msg}".encode("utf-8"))  # Send private message command
        else:
            self.sock.send(message.encode("utf-8"))  # Send as public message
        self.input_area.delete('1.0', 'end')

        # Reset cursor position to the beginning of the input area
        self.input_area.mark_set(tkinter.INSERT, "1.0")

    def get_active_users(self):
        self.sock.send('/active_users'.encode("utf-8"))
        

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode("utf-8")
                if message == 'NICK':
                    self.sock.send(self.nickname.encode("utf-8"))
                else:
                    if self.gui_done:
                        if message.startswith("Online users:"):
                            self.text_area.config(state="normal")
                            self.text_area.insert("end", message + '\n')
                            self.text_area.yview("end")
                            self.text_area.config(state="disabled")
                        else:
                            self.text_area.config(state="normal")
                            self.text_area.insert("end", message + '\n')
                            self.text_area.yview("end")
                            self.text_area.config(state="disabled")
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break

    
    

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)
client = Client(host, port)


