import mss.tools
import socket
import base64
import json

def send(s : socket.socket, data : str):
    data = data.encode("utf-8")
    s.send(data)