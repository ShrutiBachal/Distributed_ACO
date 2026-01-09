%%writefile paxos/learner.py
import asyncio
from core.message import Message,MsgType

class Learner:
    def __init__(self, node):
        self.node = node
        self.accepted = {}   # pid → set(acceptors)
        self.majority = (len(node.peers) // 2) + 1

    async def on_accepted(self, msg):
        pid = msg.proposal_id

        if pid not in self.accepted:
            self.accepted[pid] = set()

        self.accepted[pid].add(msg.src)

        print(
            f"[LEARNER {self.node.node_id}] "
            f"ACCEPTED msg from {msg.src}, "
            f"count_accepted={len(self.accepted[pid])}"
        )

        if len(self.accepted[pid]) >= self.majority:
            print(
                f"[LEARNER {self.node.node_id}] "
                f"VALUE CHOSEN = {msg.value}"
            )
