from .exceptions import *
from .user import User

class UserList:
    def __init__(self):
        self.users = {}
        self.screenshare = {"active": False, "by": None, "finishedLastFrameTimestamp": 0}
        self.lastImage = None

    def add_user(self, user : User):
        self.users[user.address[1]] = user
        if self.screenshare["active"]: user.send("user_started_screensharing")

        self.send("user_connected", data={"id": user.address[1]}, exclude=[user.address])

    def remove_user(self, id : str):
        user = self.users[id]
        if self.screenshare["active"] and self.screenshare["by"].address == user.address:
            self.screenshare = {"active": False, "by": None, "finishedLastFrameTimestamp": 0}
            self.send("user_stopped_screensharing", exclude=[user.address])

        self.send("user_disconnected", data={"id": user.address[1]}, exclude=[user.address])
        self.users.pop(id)

    def send(self, action : str, *, data : dict = {}, exclude : list = []):
        for user in self.users.values():
            if user.address in exclude: continue

            user.send(action, data)
    
    def start_screensharing(self, by : User):
        if self.screenshare["active"]: raise AlreadyScreensharing("A user is already screensharing")

        self.screenshare = {"active": True, "by": by, "finishedLastFrameTimestamp": 0}
        by.send("started_screensharing_successfully")
        self.send("user_started_screensharing", exclude=[by.address])
    
    def stop_screensharing(self, by):
        if not self.screenshare["active"]: raise NotScreensharing("No one is screensharing")
        if self.screenshare["by"].address != by.address: raise NotScreensharing("You are not screensharing")

        self.screenshare["active"] = False
        by.send("stopped_screensharing_successfully")
        self.send("user_stopped_screensharing", exclude=[by.address])