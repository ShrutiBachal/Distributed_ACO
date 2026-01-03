%%writefile simulation/test_network.py
import asyncio

from core.network import Network
from core.node import Node
from core.message import Message

async def main():
    network = Network()

    n1 = Node(1, network)
    n2 = Node(2, network)

    network.register(n1)
    network.register(n2)

    #asyncio.create_task(n1.run())
    asyncio.create_task(n2.run())

    msg = Message( # You can change source and dest to change sender and receiver
        msg_type="TEST",
        src=1,
        dst=2,
        value="Hello from Node 1"
    )
    msg1 = Message( # You can change source and dest to change sender and receiver
        msg_type="TEST",
        src=3,
        dst=2,
        value="Hello from Node 3"
    )

    await network.send(msg)
    await asyncio.sleep(1)

    await network.send(msg1)
    await asyncio.sleep(1)

# def run_async(coro):
#     try:
#         import asyncio
#         loop = asyncio.get_running_loop()
#         return coro
#     except RuntimeError:
#         import asyncio
#         return asyncio.run(coro)
