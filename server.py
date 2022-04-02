import datetime
import socket
import threading

from logger import logger
from message import Message
from response_code import ResponseCode


class Server:
    """A class that handles user conncetion and servers messages to all the clients."""
    PORT: int = 5050
    SERVER: str = socket.gethostbyname(socket.gethostname())
    ADDR: tuple = (SERVER, PORT)
    
    def __init__(self) -> None:
        """initializes the server and some cointiners for users and nicknames."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.nicknames: set = set()
        self.clients: set[socket.socket] = set()
        self.clients_lock = threading.Lock()
    
    def bad_nickname(self, nickname: str) -> bool:
        """Checks if the provided nickname matches a nickname already registered,
        if so returns True, otherwise adds the nickname to the list and returns False."""
        if nickname in self.nicknames:
            return True
        else:
            self.nicknames.add(nickname)
            return False
    
    def broadcast(self, nickname: str, msg: str) -> None:
        """Takes a nickname and message, then sends it to all the clients in the client set."""
        logger.info(f"[{nickname}] {msg}")
        new_msg = "{} [{}] {}".format(
                    datetime.datetime.now().strftime("%H:%M:%S"), nickname, msg)
        with self.clients_lock:
            for conn in self.clients:
                self.send(conn, new_msg)

    def send(self, conn: socket.socket, msg: str):
        message = Message()
        message.body = msg
        conn.sendall(message.body.encode(Message.FORMAT))
    
    def send_welcome(self, conn: socket.socket, nickname: str):
        message = "{} [CONNECTED] Connection successful! Welcome {}.".format(
                    datetime.datetime.now().strftime("%H:%M:%S"), nickname)
        self.send(conn, message)
                
    def handle_client(self, conn: socket.socket, nickname: str) -> None:
        """Acts the client thread, handling all the message, and disconnect events."""
        try:
            self.send_welcome(conn, nickname)
            while True:
                message = Message()
                message_len = conn.recv(Message.HEADER)
                if not message_len:continue
                header = message_len.decode(Message.FORMAT)
                message.body = conn.recv(int(header)).decode(Message.FORMAT)
                if not message.body:break
                if message.body == Message.DISCONNECT:break
                self.broadcast(nickname, message.body)
        except ConnectionResetError:
            logger.error(f"[ERROR] Connection reset by {nickname}'s client.")
        finally:
            with self.clients_lock:
                self.clients.remove(conn)
            conn.close()
            self.nicknames.remove(nickname)
            logger.info(f"[SERVER] {nickname} Disconnected...")
            logger.info("[ACTIVE CONNECTIONS] {}".format(len(self.clients)))
            self.broadcast("SERVER", f"{nickname} Disconnected...")

    def start(self) -> None:
        """Start the server listening for client connections, and handles new connections."""
        logger.info(f"[STARTING] server is starting @ {self.SERVER}")
        self.server.listen()
        while True:
            conn, _ = self.server.accept()
            nickname = conn.recv(Message.HEADER).decode(Message.FORMAT).title()
            if self.bad_nickname(nickname):
                conn.sendall(str(ResponseCode.REJECTED.name).encode(Message.FORMAT))
                continue
            conn.sendall(str(ResponseCode.ACCEPTED.name).encode(Message.FORMAT))
            self.broadcast("SERVER", f"{nickname} joined the chat...")
            with self.clients_lock:
                self.clients.add(conn)
            thread = threading.Thread(target=self.handle_client, args=(conn, nickname), daemon=True)
            thread.start()
            logger.info(f"[NEW CONNECTION] {nickname} Connected...")
            logger.info("[ACTIVE CONNECTIONS] {}".format(len(self.clients)))


if __name__ == "__main__":
    try:
        server = Server()
        server.start()
    except KeyboardInterrupt:
        print("\033[1A")
        logger.info("[STOPPING] server stopped...goodbye")
