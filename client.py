import selectors
import socket
import sys
import threading


class Client:
    """This class acts as the cleint object handling the client side of the connection."""
   
    def __init__(self, nickname: str):
        """Initializes the attributes needed to host the client instance."""
        self.FORMAT: str = "utf-8"
        self.DISCONNECT_MSG: str = "!DISCONNECT"
        self.HEADER:int = 64
        self.ACCEPTED = 200
        self.REJECTED = 400
        
        PORT: int = 5050
        SERVER = socket.gethostbyname(socket.gethostname())
        ADDR: tuple = (SERVER, PORT)

        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        self.verify_nickname(nickname)

    def verify_nickname(self, nickname: str):
        """this method handles the return code from the server verifying a good nickname."""
        self.client.send(nickname.encode(self.FORMAT))
        recv = int(self.client.recv(1024).decode(self.FORMAT).strip())
        if recv is self.ACCEPTED:self.main()
        if recv == self.REJECTED:
            raise Exception(f"Nickname {nickname} already in use, please try again...")
        
    def recieve(self, bytes: int = 2046):
        """this method listens for broadcast from the server and returns them to the client."""
        recv = self.client.recv(bytes).decode(self.FORMAT)
        if recv:print(recv)
            
    def msg_len(self, msg: str):
        """this method returns the length of the in bytes for the HEADER message."""
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode((self.FORMAT))
        send_length += b" " * (self.HEADER - len(send_length))
        return send_length
        
    def get_message(self):
        """This method waits for the user to input a message, then passes the string to the handle_message method."""
        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ)
        sys.stdout.flush()
        pairs = sel.select(timeout=1)
        if pairs:self.handle_message()

    def handle_message(self):
        """this method takes the user input string and sends it to the send_msg method."""
        msg = sys.stdin.readline().strip()
        sys.stdout.write("\033[1A\033[K")
        if msg:
            if msg == "!disconnect":
                self.disconnect()
            self.send_msg(msg)

    def send_msg(self, message: str):
        """this method takes the user input string, sends the length in a header msg, then sends the user string to the server."""
        self.client.send(self.msg_len(message))
        self.client.send(message.encode(self.FORMAT))
    
    def disconnect(self):
        """this method handlers the disconnection of the client from the server and closes the cleint program."""
        self.running = False
        self.send_msg(self.DISCONNECT_MSG)
        print("[USER] Disconnected...")
        sys.exit()

    def thread(self, method):
        """This method instanciates a daemon thread for the passed method"""
        TIMEOUT: float = 0.5
        stop_event = threading.Event()
        thread_lock = threading.Lock()
        thread = threading.Thread(target=method, daemon=True)
        with thread_lock:
            thread.start()
            thread.join(timeout=TIMEOUT)
            stop_event.set()

    def main(self):
        """this method acts as the main loop for the client, pass the get_message, and recieve method to the thread method."""
        self.running = True
        while self.running:
            self.thread(self.get_message)
            self.thread(self.recieve)

        
if __name__ == "__main__":
    client = Client(input("What is your Nickname..."))
    
