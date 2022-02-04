# Python Chat
### this project is socket based chat server.

##### To run this project run the  > server.py file first. 

##### Then run two instances of the > client.py file 

##### To close the client conncection send the "!disconnect" message and the connection will be closed.

##### To stop the server use a Keyboard Interrupt (CTL+C) to shut down the server.

these two clients will be the ones communitcating, the server just handles the events and logs the chat.

run the file and input a Nickname to use as a username.
the server will check if the nick is already in use and return a unable to connect code.

The server should dynamicly retrive the local IP address, then start the server to accept connections and handle the clients as indivual threads.


this server client combo are build completely from standard python packages.

Author: Jason Stayner
2022
