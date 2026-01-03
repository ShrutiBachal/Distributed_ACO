%%writefile core/message.py
from enum import Enum

class MsgType(Enum):
    PREPARE = 1
    PROMISE = 2
    ACCEPT = 3
    ACCEPTED = 4
    LEARN = 5

class Message:
    def __init__(self, msg_type, src, dst, value, proposal_id=None):  # Order of args matter non-default should be before default
        self.msg_type = msg_type
        self.src = src
        self.dst = dst
        self.proposal_id = proposal_id
        self.value = value
