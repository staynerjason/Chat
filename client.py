import datetime
import socket
import sys
import threading

from message import  Message
from response_code import BadNickname, ResponseCode


class Client:
    """A client class to connect to the server and send and receive messages."""
    PORT: int = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR: tuple = (SERVER, PORT)

    def __init__(self, nickname: str) -> None:
        """Initialize the client socket and connets the server."""
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.ADDR)
        self.nickname: str = nickname

    def recieve(self) -> None:
        """Recieves a message from the server, and prints the message."""
        body = self.conn.recv(1024).decode(Message.FORMAT)
        if body: print(body)

    def message_handler(self):
        """A method that handles the message sending operations.""" 
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
    
    def send_msg(self, message: Message) -> None:
        """Takes a message sends the size to the server, then sends the message."""
        self.conn.send(message.parse_header())
        self.conn.send(message.body.encode(Message.FORMAT))

    def verify_nickname(self) -> None:
        """Handles the handshake with the server verifying a good nickname was provided."""
        self.conn.send(self.nickname.encode(Message.FORMAT))
        recv = self.conn.recv(Message.HEADER).decode(Message.FORMAT)
        code = ResponseCode[recv]
        if code is ResponseCode.REJECTED:
            raise BadNickname(
                f"Nickname {self.nickname} already in use, please try again...")
        if code is not ResponseCode.ACCEPTED:
            raise Exception("An error occurred while verifying your nickname, please try again...")
       

def main() -> None:
    """A Main function that instantiates a cliend and runs the main loop."""
    try:
        client = Client(input("What is your Nickname..."))
        client.verify_nickname()
        TIMEOUT: float = 0.5
        stop_event = threading.Event()
        thread_lock = threading.Lock()
        while True:
            recv = threading.Thread(target=client.recieve, daemon=True)
            with thread_lock:
                recv.start()
                recv.join(timeout=TIMEOUT)
                stop_event.set()

            msg = threading.Thread(target=client.message_handler, daemon=True)
            with thread_lock:
                msg.start()
                msg.join(timeout=TIMEOUT)
                stop_event.set()

    except ConnectionResetError as e:
        print(f"[ERROR] Connection reset by server")
    except BrokenPipeError as e:
        print(f"[ERROR] Failed to connect to server...")
    except BadNickname as e:
        print(e)
    except ConnectionRefusedError as e:
        print(f"[ERROR] Connection refused by server...")
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
