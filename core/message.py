%%writefile core/message.py
from enum import Enum

class MsgType(Enum):
    PREPARE = "PREPARE"
    PROMISE = "PROMISE"
    ACCEPT = "ACCEPT"
    ACCEPTED = "ACCEPTED"
    LEARN = "LEARN"

class Message:
    def __init__(self, msg_type, src, dst, value = None, proposal_id = None,accepted_id = None):  # Order of args matter non-default should be before default
    # Making it None allows the value to be optional i.e., no compulsion to always declare it
        self.msg_type = msg_type
        self.src = src
        self.dst = dst
        self.proposal_id = proposal_id
        self.value = value
        self.accepted_id = accepted_id

    def __repr__(self):
        return (f"{self.msg_type} "
                f"from {self.src} "
                f"pid={self.proposal_id} "
                f"value={self.value}")
