%%writefile paxos/proposer.py
import asyncio
from core.message import Message,MsgType

class Proposer:
    def __init__(self, node):
        self.node = node
        self.promises = {}
        self.proposal_seq = 0
        self.proposed_value = None

    async def propose(self, value):
      print(f"[PROPOSER {self.node.node_id}] Proposing value={value}")
      self.proposal_seq += 1  # each time it proposes, seq value increases by 1
      proposal_id = (self.proposal_seq, self.node.node_id)

      self.promises.clear()

      for peer in self.node.peers:
          msg = Message(
          MsgType.PREPARE,
          src=self.node.node_id,
          dst=peer,
          proposal_id=proposal_id,
        )
        asyncio.create_task(self.node.network.send(msg))

    async def on_promise(self, msg):
        pid = msg.proposal_id

        # collect promises
        if pid not in self.promises:
            self.promises[pid] = []

        self.promises[pid].append(msg)
        majority = (len(self.node.peers) // 2) + 1

        # only act once, exactly at majority
        if len(self.promises[pid]) == majority:
          # Paxos value selection rule
          highest = None
          chosen_value = self.proposed_value
          for p in self.promises[pid]:
            if p.value is not None:
                if highest is None or p.accepted_id > highest[0]:
                    highest = (p.accepted_id, p.value)

          if highest:
            chosen_value = highest[1]

          print(f"[PROPOSER {self.node.node_id}] Chosen value={chosen_value}")

          # send ACCEPT to all peers
          for peer in self.node.peers:
            acc = Message(
                MsgType.ACCEPT,
                src=self.node.node_id,
                dst=peer,
                proposal_id=pid,
                value=chosen_value
            )
            asyncio.create_task(self.node.network.send(acc))

