import socket
import threading
import selectors
import sys


class Client:
    def __init__(self, nickname: str):
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
        self.client.send(nickname.encode(self.FORMAT))
        recv = int(self.client.recv(1024).decode(self.FORMAT).strip())
        if recv is self.ACCEPTED:self.main()
        if recv == self.REJECTED:
            raise Exception(f"Nickname {nickname} already in use, please try again...")
        
              
    def recieve(self, bytes: int = 2046):
        recv = self.client.recv(bytes).decode(self.FORMAT)
        if recv:print(recv)
            
    def msg_len(self, msg: str):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode((self.FORMAT))
        send_length += b" " * (self.HEADER - len(send_length))
        return send_length

    def get_message(self):
        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ)
        sys.stdout.flush()
        pairs = sel.select(timeout=1)
        if pairs:self.handle_message()

    def handle_message(self):
        msg = sys.stdin.readline().strip()
        sys.stdout.write("\033[1A\033[K")
        if msg:
            if msg == "!disconnect":
                self.disconnect()
            self.send_msg(msg)

    def disconnect(self):
        self.RUNNING = False
        self.send_msg(self.DISCONNECT_MSG)
        print("[USER] Disconnected...")
        sys.exit()
    
    def send_msg(self, message: str):
        self.client.send(self.msg_len(message))
        self.client.send(message.encode(self.FORMAT))

    def main(self):
        self.RUNNING = True
        TIMEOUT: float = 0.5
        stop_event = threading.Event()
        thread_lock = threading.Lock()
        while self.RUNNING:
            recv = threading.Thread(target=self.recieve, daemon=True)
            with thread_lock:
                recv.start()
                recv.join(timeout=TIMEOUT)
                stop_event.set()

            msg = threading.Thread(target=self.get_message, daemon=True)
            with thread_lock:
                msg.start()
                msg.join(timeout=TIMEOUT)
                stop_event.set()
        
        


if __name__ == "__main__":
    client = Client(input("What is your Nickname..."))
    
