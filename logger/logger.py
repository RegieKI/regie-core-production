from enum import Enum

class LogType(Enum):
    NOTICE  = 1
    WARNING = 2
    ERROR   = 3

# Singleton/ClassVariableSingleton.py
class Logger(object):
    __instance = None

    def __init__(self):
        self.channels = [
            print
        ]

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
        return Logger.__instance

    def log(self, msg, logType = LogType.NOTICE ):
        for callback in self.channels:
            callback(msg)

    def add_channel(self, callback):
        self.channels.append(callback)