%%writefile paxos/proposer.py
import asyncio
from core.message import Message,MsgType

class Proposer:
    def __init__(self, node):
        self.node = node
        self.promises = {}
        self.proposal_seq = 0
        self.proposed_value = None
        self.timeout = None
        self.timeout_tasks = {}  # proposal_id -> asyncio.Task

    async def propose(self, value):
     
      self.proposal_seq += 1  # each time it proposes, seq value increases by 1
      proposal_id = (self.proposal_seq, self.node.node_id)
      self.proposed_value = value
      self.promises[proposal_id] = []

      print(f"[PROPOSER {self.node.node_id}] Proposing value={value} with [Pid {proposal_id}")
      for peer in self.node.peers:
          msg = Message(
          MsgType.PREPARE,
          src=self.node.node_id,
          dst=peer,
          proposal_id=proposal_id,
        )
        asyncio.create_task(self.node.network.send(msg))

      # start timeout watcher
      self.timeout_tasks[proposal_id] = asyncio.create_task(
         self._on_timeout(proposal_id,1.5)
      )

   async def _on_timeout(self, proposal_id,timeout):
        await asyncio.sleep(timeout)

        # If still not enough promises, retry
        if len(self.promises.get(proposal_id, [])) <= len(self.node.peers) // 2:
            print(f"[PROPOSER {self.node.node_id}] TIMEOUT pid={proposal_id}, retrying")

            # clean up
            self.promises.pop(proposal_id, None)
            self.timeout_tasks.pop(proposal_id, None)

            if self.node.decided:
              return  # consensus already reached

            # retry with higher proposal number
            await self.propose(self.proposed_value)

    async def on_promise(self, msg):
        pid = msg.proposal_id

        # collect promises
        if pid not in self.promises:
            print(f"[PROPOSER {self.node.node_id}] STALE PROMISE ignored pid={pid}")
            return

        self.promises[pid].append(msg)
        majority = (len(self.node.peers) // 2) + 1
        print(f"[PROPOSER {self.node.node_id}] PROMISE from {msg.src} pid={pid}")

        if len(self.promises[pid]) >= majority:
          # cancel timeout
          if pid in self.timeout_tasks:
              self.timeout_tasks[pid].cancel()
              self.timeout_tasks.pop(pid, None)
              
          # Paxos value selection rule
          highest = None
          chosen_value = self.proposed_value
          for p in self.promises[pid]:
            if p.value is not None:
                if highest is None or p.accepted_id > highest[0]:
                    highest = (p.accepted_id, p.value)

          if highest:
            chosen_value = highest[1]

          print(f"[PROPOSER {self.node.node_id}] MAJORITY pid={pid} Chose value={chosen_value}, sending ACCEPT")
            
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

          # clean promise state
          self.promises.pop(pid, None)
            
          # wait for ACCEPTED majority
          ok = await self.wait_for_learner(timeout=4.0)
          if ok:
            self.node.decided = True
            print("Consensus finished")
            return
          self.propose(chosen_value)

    async def wait_for_learner(self,timeout):
        try:
            await asyncio.wait_for(self.node.learner.learned_event.wait(), timeout=timeout)
            print(f"[LEARNER {self.node.node_id}] confirmed value = {self.node.learner.learned_value}")
            return True

        except asyncio.TimeoutError:
            print("Accept phase stalled, restarting with higher pid")   # go back to PREPARE with higher pid


