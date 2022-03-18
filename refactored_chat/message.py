import datetime
import socket
import sys

from selectors import DefaultSelector, EVENT_READ


class Message:
    """A message object that will be sent to the server"""
    HEADER:int = 64
    body:str = ""
    DISCONNECT:str = '!DISCONNECT'
    FORMAT:str = 'utf-8'    
    
    def check_input(self) -> bool:
        """A method that checks if a message has been typed into the terminal."""
        selector = DefaultSelector()
        selector.register(sys.stdin, EVENT_READ)
        sys.stdout.flush
        if selector.select(timeout=1):
            return True
        return False

    def get_input(self) -> None:
        """A method that gets the text from the terminal and clears the input box."""
        self.body = sys.stdin.readline().strip()
        sys.stdout.write("\033[1A\033[K")

    def get_header(self) -> bytes:
        """A method that evaluates the size if the message in bytes and returns the value."""
        msg = self.body.encode(self.FORMAT)
        msg_length = len(msg)
        send_length = str(msg_length).encode((self.FORMAT))
        send_length += b" " * (self.HEADER - len(send_length))
        return send_length


class MessageHandler:
    """A Class that handles the message sending operations.""" 
    def __init__(self, conn:socket.socket) -> None:
        """Takes in a client conncetion and send the message."""
        self.conn = conn
        message = Message()
        if message.check_input():
            message.get_input()    
            if message.body != "":
                self.send_msg(message)        
            print("\033[1A")
                
    def disconnect(self) -> None:
        """Disconnects from the server."""
        disconnect_msg = Message()
        disconnect_msg.body = Message.DISCONNECT
        self.send_msg(disconnect_msg)
        print("\033[1A")
        print("{} [USER] Disconnected...".format(datetime.datetime.now().strftime("%H:%M:%S")))
        sys.exit()
    
    def send_msg(self, message:Message) -> None:
        """Takes a message sends the size to the server, then sends the message."""
        self.conn.send(message.get_header())
        self.conn.send(message.body.encode(Message.FORMAT))