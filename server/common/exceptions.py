class AlreadyScreensharing(Exception):
    def __init__(self, message : str) -> None:
        """
        You are trying to start a screenshare but a screenshare is already active.
        """

        super().__init__(message)

class NotScreensharing(Exception):
    def __init__(self, message : str) -> None:
        """
        You are trying send an action on a screenshare that either doesn't exist or you are not controlling
        """

        super().__init__(message)