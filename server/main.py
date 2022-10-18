from PIL import Image
from common import *

import multiprocessing
import threading
import socket
import base64
import time
import ast
import io

def handle_client(connection : socket.socket, address : tuple):
    print(f"{address} connected")
    user = User(connection, address)
    userList.add_user(user)

    while True:
        try: data = connection.recv(16784000)
        except (ConnectionResetError, ConnectionAbortedError):
            print(f"{address} disconnected")
            connection.close()
            userList.remove_user(address[1])
            return
        if not data:
            print(f"{address} disconnected")
            connection.close()
            userList.remove_user(address[1])
            return
        
        data = data.decode("utf-8")
        commands = data.split("}{")
        for command in commands:
            if not command.endswith("}"): command += "}"
            if not command.startswith("{"): command = "{" + command
            handle_command(command, user)


def handle_command(command : dict, user : User):
    timestamp = time.time()
    try: data = ast.literal_eval(command)
    except (ValueError, SyntaxError):
        user.send("error", {"message": "Data must be a dict", "error": "InvalidData"})
        return

    if not isinstance(data, dict):
        user.send("error", {"message": "Data must be a dict", "error": "InvalidData"})
        return
    elif not "action" in data:
        user.send("error", {"message": "Missing Action", "error": "MissingAction"})
        return
    elif not data["action"] in ACTIONS:
        user.send("error", {"message": "Invalid Action", "error": "InvalidAction"})
        return
    
    missingArguments = [argument for argument in ACTIONS[data["action"]].keys() if not argument in data]
    if missingArguments:
        user.send("error", {"message": f"Missing Argument{'s' if len(missingArguments) != 1 else ''}: {', '.join(missingArguments)}", "error": "MissingArguments"})
        return

    invalidTypes = [f"{argument}: {type.__name__}" for argument, type in ACTIONS[data["action"]].items() if not isinstance(data[argument], type)]
    if invalidTypes:
        user.send("error", {"message": f"Invalid argument type: {', '.join(invalidTypes)}", "error": "InvalidType"})
        return
    
    if data["action"] == "start_screenshare":
        try: userList.start_screensharing(user)
        except AlreadyScreensharing:
            user.send("error", {"message": f"Another user is already screensharing" if userList.screenshare["by"].address != user.address else "You are already screensharing", "error": "AlreadyScreensharing"})
            return
    elif data["action"] == "stop_screenshare":
        try: userList.stop_screensharing(user)
        except NotScreensharing:
            user.send("error", {"message": "A screenshare either isn't running or you are not controlling it", "error": "NotScreensharing"})
            return
    elif data["action"] == "send_screenshare_image":
        if not userList.screenshare["active"] or userList.screenshare["by"].address != user.address:
            user.send("error", {"message": "A screenshare either isn't running or you are not controlling it", "error": "NotScreensharing"})
            return

        image = Image.open(io.BytesIO(base64.b64decode(data["image"])))
        if max(image.size) > 274:
            divide = max(image.size) / 274
            image = image.resize((int(image.size[0] / divide), int(image.size[1] / divide)), Image.NEAREST)
        
        if userList.lastImage == data["image"]:
            user.send(action="sent_image_successfully")
            return
        userList.lastImage = data["image"]
        
        pixels = numpy.asarray(image)
        pool = multiprocessing.Pool(processes=6)
        result = base64.b64encode("\n".join(pool.map(image_to_text, pixels)).encode("unicode-escape")).decode("utf-8")
        
        userList.screenshare["finishedLastFrameTimestamp"] = time.time()
        userList.send(action="screenshare_image", data={"image": result}, exclude=[user.address])
        user.send(action="sent_image_successfully")

def main():
    print(f"Server ready on IP {IP}:{PORT}")
    while True:
        connection, address = s.accept()
        threading.Thread(target=handle_client, args=(connection, address), daemon=True).start()

if __name__ == "__main__":
    ACTIONS = {
        "start_screenshare": {},
        "stop_screenshare": {},
        "send_screenshare_image": {"image": str}
    }

    IP = socket.gethostbyname(socket.gethostname())
    PORT = 6969

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind(("0.0.0.0", PORT))
    s.listen(socket.SOMAXCONN)

    userList = UserList()
    
    main()