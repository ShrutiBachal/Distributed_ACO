%%writefile paxos/proposer.py
import asyncio
from core.message import Message,MsgType

class Proposer:
    def __init__(self, node):
        self.node = node
        self.promises = {}
        self.proposal_seq = 0

    async def propose(self, value):
      print(f"[PROPOSER {self.node.node_id}] Proposing value={value}")
      self.proposal_seq += 1  # each time it proposes, seq value increases by 1
      proposal_id = (self.proposal_seq, self.node.node_id)

      self.promises = {}

      for peer in self.node.peers:
          msg = Message(
          MsgType.PREPARE,
          src=self.node.node_id,
          dst=peer,
          proposal_id=proposal_id,
      )
      asyncio.create_task(self.node.network.send(msg))

    async def on_promise(self, msg):
        if msg.proposal_id not in self.promises:
            self.promises[msg.proposal_id] = []

        self.promises[msg.proposal_id].append(msg)

        if len(self.promises[msg.proposal_id]) > len(self.node.peers) // 2:
            chosen_value = msg.value if msg.value else "DEFAULT"

            for peer in self.node.peers:
                acc = Message(
                    MsgType.ACCEPT,
                    src=self.node.node_id,
                    dst=peer,
                    proposal_id=msg.proposal_id,
                    value=chosen_value
                )
                asyncio.create_task(self.node.network.send(acc))

