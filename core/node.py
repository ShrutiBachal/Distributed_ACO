%%writefile core/node.py
import asyncio
from core.message import MsgType, Message
from paxos.proposer import Proposer
from paxos.acceptor import Acceptor
from paxos.learner import Learner

class Node:
    def __init__(self, node_id, network, peers):
        self.node_id = node_id
        self.network = network
        self.inbox = asyncio.Queue()
        self.peers = peers

        # Paxos state (Acceptor)
        self.acceptor = Acceptor(self)

        # Paxos state (Proposer)
        self.proposer = Proposer(self)

        # Paxos state (Learner)
        self.learner = Learner(self)

    async def run(self):
        while True:
            msg = await self.inbox.get()
            if self.network.consensus_reached:
              return
                
            if msg.run_id != self.network.run_id:       # ignore msgs which do not belong to current run
              print(
                  f"[NODE {self.node_id}] Ignoring stale message "
                  f"(msg run={msg.run_id}, current run={self.network.run_id})"
              )
              continue
                
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
          await self.proposer.on_accepted(msg)
          await self.learner.on_accepted(msg)
