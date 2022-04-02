import sys

from selectors import DefaultSelector, EVENT_READ


class Message:
    """A message object that will be sent to the server"""
    HEADER:int = 64
    DISCONNECT:str = '!DISCONNECT'
    FORMAT:str = 'utf-8'    
    body:str = ""
    
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
    
    def parse_header(self) -> bytes:
        """A method that evaluates the size if the message in bytes and returns the value."""
        send_length = str(len(self.body)).encode((self.FORMAT))
        send_length += b" " * (self.HEADER - len(send_length))
        return send_length