import socket
import threading


class Server:
    """This class handles the conncection of clients, broadcasting of client messeges and handling the nickname namespace."""
    def __init__(self):
        """Initialize attributes needed for the server"""
        self.PORT: int = 5050
        self.SERVER: str = socket.gethostbyname(socket.gethostname())
        self.ADDR: tuple = (self.SERVER, self.PORT)
        self.FORMAT: str = "utf-8"
        self.HEADER: int = 64
        self.DISCONNECT_MSG: str = "!DISCONNECT"
        self.ACCEPTED:str = str(200)
        self.REJECTED:str = str(400)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

        self.nicknames:set = set()
        self.clients: set = set()
        self.clients_lock = threading.Lock()

    def handle_client(self, conn, nickname):
        """this method takes in a client thead and handles the incoming messages,
        as well as broadcasting the messages to all the other clients."""
        try:
            connected = True
            conn.send(
                f"[CONNECTED] Connection successful! Welcome {nickname}.".encode(self.FORMAT))
            while connected:
                msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
                if msg_length:
                    msg = conn.recv(int(msg_length)).decode(self.FORMAT)
                    if not msg:
                        break
                    if msg == self.DISCONNECT_MSG:
                        break
                    print(f"[{nickname}] {msg}")
                    self.broadcast(nickname, msg)
        finally:
            with self.clients_lock:
                self.clients.remove(conn)
            conn.close()
            self.nicknames.remove(nickname)
            print(f"[SERVER] {nickname} Disconnected...")
            print(f"[ACTIVE CONNECTIONS] {self.active_connections - 1}")
            self.broadcast("SERVER", f"{nickname} Disconnected...")

    def broadcast(self, nickname, msg):
        """this method takes in a client nickname and the message, 
        then sends the messages to all the client threads in the client set."""
        with self.clients_lock:
            for c in self.clients:
                c.sendall(f"[{nickname}] {msg}".encode(self.FORMAT))

    def bad_nickname(self, nickname):
        """this method verify that the nickname of the new connection is not in the nicknames set already.
        If the nickname is not in the set, then the nick name will be added to the set."""
        if nickname in self.nicknames:
            return True
        else:self.nicknames.add(nickname)

    def start(self):
        """this method acts as the server main loop, waiting for incomming connections, 
        then handling the initialzation of the client as a new thread and passing the client to the handle client method"""
        print(f"[STARTING] server is starting @ {self.SERVER}")
        self.server.listen()
        while True:
            conn, _ = self.server.accept()
            nickname = conn.recv(self.HEADER).decode(self.FORMAT).title()
            if self.bad_nickname(nickname):
                conn.send(self.REJECTED.encode(self.FORMAT))
                continue
            conn.send(self.ACCEPTED.encode(self.FORMAT))
            self.broadcast("SERVER", f"{nickname} joined the chat...")
            with self.clients_lock:
                self.clients.add(conn)
            thread = threading.Thread(target=self.handle_client, args=(conn, nickname))
            thread.start()
            print(f"[NEW CONNECTION] {nickname} Connected...")
            self.active_connections = threading.activeCount() - 1
            print(f"[ACTIVE CONNECTIONS] {self.active_connections}")

    def stop(self):    
        print("\033[1A")
        print("[STOPPING] server stopped...goodbye")


if __name__ == "__main__":
    try:
        server = Server()
        server.start()
    except KeyboardInterrupt:
        server.stop()
