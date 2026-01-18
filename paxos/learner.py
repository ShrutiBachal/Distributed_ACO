%%writefile paxos/learner.py
import asyncio
from core.message import Message,MsgType

class Learner:
    def __init__(self, node):
        self.node = node
        self.accepted = {}   # pid → set(acceptors)
        self.majority = (len(node.peers) // 2) + 1
        self.learned_event = asyncio.Event()
        self.learned_pid = None
        self.learned_value = None

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

        if len(self.accepted[pid]) >= self.majority:    # majority = 1 more than half of peers
            self.learned_pid = pid
            self.learned_value = msg.value
            print(f"[LEARNER {self.node.node_id}] Learned {msg.value}")
            self.learned_event.set()
            
            if self.node.network.visualizer:
              self.node.network.visualizer.learned(
              self.node.node_id,msg.value
            )
