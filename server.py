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
    FORMAT: str = "utf-8"
    DISCONNECT_MSG: str = "!DISCONNECT"

    def __init__(self) -> None:
        """initializes the server and some cointiners for users and nicknames."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.nicknames: set = set()
        self.clients: set[socket.socket] = set()
        self.clients_lock = threading.Lock()
    
    def bad_nickname(self, nickname) -> bool:
        """Checks if the provided nickname matches a nickname already registered,
        returns True if it is, otherwise adds the nickname to the list and returns False."""
        if nickname in self.nicknames:
            return True
        else:
            self.nicknames.add(nickname)
            return False
    
    def broadcast(self, nickname, msg) -> None:
        """Takes a nickname and message, then sends it to all the clients in the client set."""
        with self.clients_lock:
            for c in self.clients:
                c.sendall("{} [{}] {}".format(
                    datetime.datetime.now().strftime("%H:%M:%S"), nickname, msg)
                    .encode(Message.FORMAT))

    def handle_client(self, conn: socket.socket, nickname: str) -> None:
        """Acts the client thread, handling all the message, and disconnect events."""
        try:
            conn.send(
                "{} [CONNECTED] Connection successful! Welcome {}.".format(
                    datetime.datetime.now().strftime("%H:%M:%S"), nickname)
                    .encode(Message.FORMAT))
            connected = True
            message = Message()
            while connected:
                message_len = conn.recv(64)
                if not message_len:continue
                header = message_len.decode(Message.FORMAT)
                message.body = conn.recv(int(header)).decode(Message.FORMAT)
                if not message.body:break
                if message.body == self.DISCONNECT_MSG:break
                logger.info(f"[{nickname}] {message.body}")
                self.broadcast(nickname, message.body)
        except ConnectionResetError:
            logger.warning(f"[ERROR] Connection reset by {nickname}'s client.")
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
                conn.send(str(ResponseCode.REJECTED.name).encode(Message.FORMAT))
                continue
            conn.send(str(ResponseCode.ACCEPTED.name).encode(Message.FORMAT))
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
