%%writefile core/network.py
import asyncio
import random
import time

class Network:
    def __init__(self, min_delay=0.1, max_delay=1.5, loss_rate=0.05,run_id = None,visualizer = None):
        self.nodes = {}
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.loss_rate = loss_rate
        self.visualizer = visualizer
        self.consensus_reached = False
        self.start_time = 0
        self.end_time = 0
        self.run_id = run_id

    def register(self, node):
        """Register a node with the network"""
        self.nodes[node.node_id] = node

    def consensus_time(self):                        # calculates the time required to reach consensus
      if self.start_time and self.end_time:
          return self.end_time - self.start_time
      return None

    def end_run(self, success):
      self.end_time = time.monotonic()

    async def send(self, message):
        if message.run_id != self.run_id:
          return
        if self.consensus_reached:
          return
        
        if self.visualizer:
            self.visualizer.record(         
                message.src,
                message.dst,
                message.msg_type.value,
                message.proposal_id[1],     # proposer_id
                message.proposal_id[0],     # round_id (1,3) (2-> round, 3->node_id)
                self.run_id
            )
            self.visualizer.draw()
            
        if self.start_time is None:
            self.start_time = time.monotonic()
            
        """Send a message with simulated delay and loss"""
        # Simulate message loss
        if random.random() < self.loss_rate:
            print(f"[NETWORK] Dropped message {message}")
            return

        # Simulate network delay
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)
        print(f"[NETWORK] Sending {message.value} with delay {delay:.2f}s")

        if message.dst in self.nodes:
            await self.nodes[message.dst].inbox.put(message)
        else:
            print(f"[NETWORK] Unknown destination {message.dst}")
