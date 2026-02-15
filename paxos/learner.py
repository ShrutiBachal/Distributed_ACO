%%writefile paxos/learner.py
import asyncio
import time
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
        visualizer = self.node.network.visualizer
        if self.decided:
          return
        if self.node.network.consensus_reached:
            return
            
        if pid not in self.accepted:
            self.accepted[pid] = []
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

            rid = msg.value["robot_id"]
            target = msg.value["target"]

            self.node.known_positions[rid] = target   # each node learns

            if self.node.node_id == rid:              # only the proposer moves
                self.node.position = target           # robot moves
                await asyncio.sleep(0.5)
                visualizer.clear_active_round(      # used for multiple proposer
                  pid[1],
                  pid[0]
                )
