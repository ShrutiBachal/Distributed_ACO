%%writefile core/node.py
import asyncio

class Node:
    def __init__(self, node_id,network):
        self.node_id = node_id
        self.network = network
        self.inbox = asyncio.Queue()

    async def run(self):
        while True:
            msg = await self.inbox.get()
            await self.handle(msg)

    async def handle(self, msg):
        print(f"Node {self.node_id} received {msg.value}")
