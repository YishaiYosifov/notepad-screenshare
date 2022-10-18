import socket
import json

class User:
    def __init__(self, connection : socket.socket, address : tuple):
        self.connection = connection
        self.address = address
    
    def send(self, action : str, data : dict = {}):
        data = {"action": action} | data
        data = json.dumps(data)
        try: self.connection.send(data.encode("utf-8"))
        except ConnectionResetError: pass