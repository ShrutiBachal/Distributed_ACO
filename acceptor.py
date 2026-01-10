%%writefile paxos/acceptor.py
import asyncio
from core.message import Message,MsgType

class Acceptor:
    def __init__(self, node):
        self.node = node
        self.promised_id = None
        self.accepted_id = None
        self.accepted_value = None

    async def on_prepare(self, msg):
      print(f"[ACCEPTOR {self.node.node_id}] PREPARE from {msg.src} pid={msg.proposal_id}")
      if (self.promised_id is None or
            msg.proposal_id > self.promised_id):

            self.promised_id = msg.proposal_id

            reply = Message(
                MsgType.PROMISE,
                src=self.node.node_id,
                dst=msg.src,
                proposal_id=msg.proposal_id,
                accepted_id=self.accepted_id,
            )
            asyncio.create_task(self.node.network.send(reply))

    async def on_accept(self, msg):
      print(f"[ACCEPTOR {self.node.node_id}] ACCEPT {msg.value} pid={msg.proposal_id}")
      if (self.promised_id is None or
            msg.proposal_id >= self.promised_id):

            self.promised_id = msg.proposal_id
            self.accepted_id = msg.proposal_id
            self.accepted_value = msg.value

            reply = Message(
                MsgType.ACCEPTED,
                src=self.node_id,
                dst=msg.src,
                proposal_id=msg.proposal_id,
                value=msg.value
            )
            asyncio.create_task(self.node.network.send(reply))
