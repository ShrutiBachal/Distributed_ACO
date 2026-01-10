%%writefile core/node.py
import asyncio
from core.message import MsgType, Message
from paxos.proposer import Proposer
from paxos.acceptor import Acceptor
from paxos.learner import Learner

class Node:
    def __init__(self, node_id,network,peers):
        self.node_id = node_id
        self.network = network
        self.inbox = asyncio.Queue()
        self.peers = peers

        # Paxos state (Acceptor)
        self.promised_id = None
        self.accepted_id = None
        self.accepted_value = None
        self.acceptor = Acceptor(self)

        # Paxos state (Proposer)
        self.proposal_seq = 0
        self.promises = {}
        self.proposer = Proposer(self)

        # Paxos state (Learner)
        self.accepted = {}
        self.majority = (len(self.peers) // 2) + 1
        self.learner = Learner(self)

    async def run(self):
        while True:
            msg = await self.inbox.get()
            print(f"[NODE {self.node_id}] received {msg.msg_type} from {msg.src}")
            await self.handle(msg)

    async def handle(self, msg):
      if msg.msg_type == MsgType.PREPARE:
          await self.acceptor.on_prepare(msg)

      elif msg.msg_type == MsgType.PROMISE:
          await self.proposer.on_promise(msg)

      elif msg.msg_type == MsgType.ACCEPT:
          await self.acceptor.on_accept(msg)

      elif msg.msg_type == MsgType.ACCEPTED:
          await self.on_accepted(msg)
