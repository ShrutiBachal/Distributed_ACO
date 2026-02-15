%%writefile paxos/proposer.py
import asyncio
import time
from core.message import Message,MsgType

class Proposer:
    def __init__(self, node):
        self.node = node
        self.promises = {}
        self.accepted = {}
        self.phase = {}
        self.proposal_seq = 0
        self.proposal_id = None 
        self.proposed_value = None
        self.timeout = None
        self.timeout_tasks = {}  # proposal_id -> asyncio.Task
        self.run_id = node.network.run_id
        self.majority = (len(node.peers) // 2) + 1

    async def propose(self, value):
        if self.node.network.consensus_reached:   # don't propose once consensus reached
          return
        if self.node.network.run_id != self.run_id:   # if event not from current execution, skip it
          return
        self.proposal_seq += 1  # each time it proposes, seq value increases by 1
        self.proposal_id = (self.proposal_seq, self.node.node_id)
        self.proposed_value = value
        self.promises[self.proposal_id] = []
        visualizer = self.node.network.visualizer

        print(f"[PROPOSER {self.node.node_id}] Proposing value={value} with [Pid {self.proposal_id}")
        if visualizer:
            visualizer.set_active_round(
                proposal_id[1], # proposer_id
                proposal_id[0]  # round_id
            )
        for peer in self.node.peers:
                msg = Message(
                MsgType.PREPARE,
                src=self.node.node_id,
                dst=peer,
                proposal_id=proposal_id
                run_id=self.node.network.run_id
            )
            asyncio.create_task(self.node.network.send(msg))
            
        self.phase[self.proposal_id] = "PREPARE"
        # start timeout watcher
        self.timeout_tasks[self.proposal_id] = asyncio.create_task(
            self._on_timeout(self.proposal_id,1.5,self.proposed_value)
        )

    async def _on_timeout(self, proposal_id,timeout):
        visualizer = self.node.network.visualizer
        if self.node.network.run_id != self.run_id:
          return
            
        await asyncio.sleep(timeout)

        if self.node.network.consensus_reached:
          return

        phase = self.phase.get(proposal_id)
        if phase is None:
            return  # proposal already cleaned up

        if phase == "PREPARE":
            if len(self.promises.get(proposal_id, [])) >= self.majority:   
                return  # succeeded, no retry

        if phase == "ACCEPT":
            if len(self.accepted.get(proposal_id, [])) >= self.majority:
                return  # succeeded, no retry

        self.promises.pop(proposal_id, None)
        self.accepted.pop(proposal_id, None)
        self.phase.pop(proposal_id, None)
        self.timeout_tasks.pop(proposal_id, None)

        if visualizer:                  
          visualizer.clear_active_round(
              self.proposal_id[1],
              self.proposal_id[0]
          )
        print(f"Proposer{proposal_id} retrying...")
        await self.propose(value)

    async def on_promise(self, msg):
        pid = msg.proposal_id

        # collect promises
        if pid not in self.promises:
            print(f"[PROPOSER {self.node.node_id}] STALE PROMISE ignored pid={pid}")
            return

        self.promises[pid].append(msg)
        print(f"[PROPOSER {self.node.node_id}] PROMISE from {msg.src} pid={pid}")

        if len(self.promises[pid]) >= majority:
            print(f"[PROPOSER {self.node.node_id}] Majority promises received")
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

            print(f"[PROPOSER {self.node.node_id}] MAJORITY pid={pid} Chosen position value={chosen_value}, sending ACCEPT")
            self.accepted[pid] = []
              
            # send ACCEPT to all peers
            for peer in self.node.peers:
              acc = Message(
                  MsgType.ACCEPT,
                  src=self.node.node_id,
                  dst=peer,
                  proposal_id=pid,
                  value=chosen_value,
                  run_id=self.node.network.run_id
              )
              asyncio.create_task(self.node.network.send(acc))
              
            self.phase[self.proposal_id] = "ACCEPT"
          
            # start timeout watcher
            self.timeout_tasks[pid] = asyncio.create_task(      # adding single pid in timeout_tasks
              self._on_timeout(pid,2,chosen_value)              # timeout diff from that of prepare phase
            )
          
            # clean promise state for current round
            self.promises.pop(pid, None)
            
    async def on_accepted(self,msg):
        pid = msg.proposal_id
        visualizer = self.node.network.visualizer   # to clear active round

        if pid not in self.accepted:    # new round, new pid so if no majority received, pid is removed form accepted
          print(f"[PROPOSER {self.node.node_id}] STALE 'ACCEPTED' ignored pid={pid}")
          return

        self.accepted[pid].append(msg.src)
        print(f"[PROPOSER {self.node.node_id}] received 'ACCEPTED' from {msg.src} pid={pid}")

        if len(self.accepted.get(pid, [])) >= self.majority:
          print(f"[PROPOSER {self.node.node_id}] Majority accept received, moving to {msg.value['target']}")

          # cancel timeout
          if pid in self.timeout_tasks:
              self.timeout_tasks[pid].cancel()
              self.timeout_tasks.pop(pid, None)
            
          if visualizer:
                visualizer.clear_active_round(
                self.proposal_id[1],
                self.proposal_id[0]
          )
