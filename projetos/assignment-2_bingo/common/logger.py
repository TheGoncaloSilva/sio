"""
`logger` package used to create a log in the format specified
by the audit logs call
"""
from datetime import datetime
import hashlib
import os
import time


class Logger:
    """
    Class Loger stores the log message and saves them in a file
    Attributes:
        - __messages: Saved log messages
        - __creation_time_stamp: Timestamp of when the class was 
        initialized, this is used to not overwrite existing logs
        and have different logs between different playing sessions
    """
    def __init__(self) -> None:
        """
        Initialize the class
        """
        self.__messages = []


        self.__creation_time_stamp: float = time.time()


    def insert(self , seq : int , text : str , signature : str) -> None:
        """
        Function used to create a new log record

        `Note:` Everytime a new entry is created, it's saved to a file
        Args:
            - seq: Seq number of the entity who originated it
            - text: Infomation of the log entry
            - sinature: signature of the log
        """
        hash_prev : str = "0"
        if len(self.__messages) > 0:
            hash : hashlib._Hash = hashlib.new('sha256')
            hash.update(str(self.__messages[-1]).encode())
            hash_prev = str(hash.hexdigest())

        self.__messages.append({'seq' : seq , 'hash(prev_entry)' : hash_prev , 'timestamp' : datetime.now().timestamp(),'text' : text , 'signature' : signature})

        self.__appendToLogFile()


    def getLog(self) -> list:
        """
        Function to get all the log messages saved
        Returns:
            - list object containing all the logs
        """
        return self.__messages[:]


    def reset(self) -> None:
        """
        Function to reset the log messages
        """
        self.__messages = []


    def __appendToLogFile(self) -> None:
        """
        Function to append the last log message onto a file
        """
        try:
            if not os.path.exists('./logs'):
                os.mkdir('./logs')
            
            f = open('./logs/playing_area_' + str(self.__creation_time_stamp) + '.log' , "a")
            f.write(str(self.__messages[-1]) + "\n")
            f.close()
        except Exception as e:
            print("[Warning] : " + e.__str__())

        