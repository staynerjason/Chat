import socket
import threading

from message import MessageHandler
from response_code import BadNickname, ResponseCode


class Client:
    """A client class to connect to the server and send and receive messages."""
    FORMAT: str = "utf-8"
    DISCONNECT_MSG: str = "!DISCONNECT"
    HEADER: int = 64
    PORT: int = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR: tuple = (SERVER, PORT)

    def __init__(self) -> None:
        """Initialize the client socket and connets the server."""
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(self.ADDR)
        self.nickname: str = ""

    def recieve(self, bytes: int = 1024) -> None:
        """Recieves a message from the server, and prints the message."""
        recv = self.conn.recv(bytes).decode(self.FORMAT)
        if recv:print(recv)

    def verify_nickname(self, nickname: str) -> None:
        """Handles the handshake with the server verifying a good nickname was provided."""
        self.conn.send(nickname.encode(self.FORMAT))
        recv = self.conn.recv(64).decode(self.FORMAT)
        code = ResponseCode[recv]
        if code is ResponseCode.REJECTED:
            raise BadNickname(
                f"Nickname {nickname} already in use, please try again...")
        if code is not ResponseCode.ACCEPTED:
            raise Exception("An error occurred while verifying your nickname, please try again...")
       
def main() -> None:
    """A Main function that instantiates a cliend and runs the main loop."""
    try:
        client = Client()
        client.verify_nickname(input("What is your Nickname..."))
        running = True
        TIMEOUT: float = 0.5
        stop_event = threading.Event()
        thread_lock = threading.Lock()
        while running:
            recv = threading.Thread(target=client.recieve, daemon=True)
            with thread_lock:
                recv.start()
                recv.join(timeout=TIMEOUT)
                stop_event.set()

            msg = threading.Thread(
                target=MessageHandler, args=[client.conn], daemon=True)
            with thread_lock:
                msg.start()
                msg.join(timeout=TIMEOUT)
                stop_event.set()

    except BadNickname as e:
        print(e)
    except ConnectionResetError:
        print(f"[ERROR] Connection reset by server")
    except BrokenPipeError:
        print(f"[ERROR] Failed to connect to server...")
    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused by server...")
    except KeyboardInterrupt:
        pass
    finally:
        m = MessageHandler(client.conn)
        m.disconnect()


if __name__ == "__main__":
    main()
