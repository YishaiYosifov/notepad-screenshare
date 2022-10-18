from common.util import *

import pywinauto
import threading
import pyperclip
import mss.tools
import keyboard
import argparse
import socket
import base64
import time
import ast
import os

def send_screen():
    global screensharing

    with mss.mss() as screen:
        while screensharing:
            image = screen.grab(screen.monitors[1])
            bytes = base64.b64encode(mss.tools.to_png(image.rgb, image.size)).decode("utf-8")

            send(s, json.dumps({"action": "send_screenshare_image", "image": bytes, "timestamp": time.time()}))

def send_action():
    while True:
        command = input()
        send(s, command)

def receive():
    while True:
        try: data = s.recv(16784000)
        except (ConnectionResetError, ConnectionAbortedError):
            print("Server Closed")
            s.close()
            os._exit(0)

        if not data:
            print("Server Closed")
            s.close()
            os._exit(0)

        data = data.decode("utf")
        commands = data.split("}{")
        for command in commands:
            if not command.endswith("}"): command += "}"
            if not command.startswith("{"): command = "{" + command
            handle_command(command)

def handle_command(command : str):
    global notepadWindow
    global screensharing

    try: data = ast.literal_eval(command)
    except (ValueError, SyntaxError): return

    if data["action"] == "user_started_screensharing":
        notepadWindow = pywinauto.Application().start("notepad.exe").UntitledNotepad
        notepadWindow.set_focus()
        
        for i in range(9): keyboard.press_and_release("ctrl+-")
    elif data["action"] == "user_stopped_screensharing":
        notepadWindow.set_focus()

        notepadWindow.type_keys("%{F4}")
        time.sleep(0.1)
        notepadWindow.type_keys("{RIGHT}")
        time.sleep(0.1)
        notepadWindow.type_keys("{ENTER}")
    elif data["action"] == "screenshare_image":
        notepadWindow.set_focus()
        
        pyperclip.copy(base64.b64decode(data["image"]).decode("unicode-escape"))
        keyboard.press_and_release("ctrl+a")
        keyboard.press_and_release("ctrl+v")
    elif data["action"] == "started_screensharing_successfully":
        screensharing = True
        threading.Thread(target=send_screen).start()
    elif data["action"] == "stopped_screensharing_successfully": screensharing = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", "-i", default="192.168.1.159")
    parser.add_argument("--port", "-p", default="6969")
    arguments = parser.parse_args()

    IP = arguments.ip
    
    PORT = arguments.port
    if not PORT.isnumeric():
        print("Port must be a number!")
        os._exit(0)
    PORT = int(PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))
    print("Connected to Server")

    notepadWindow = None
    screensharing = False

    threading.Thread(target=receive, daemon=True).start()
    send_action()