import asyncio
import matplotlib.pyplot as plt

plt.ion()  # interactive mode

from simulation.visualizer import PaxosVisualizer
from core.network import Network
from core.node import Node

async def main():
    net = Network(min_delay=0.05, max_delay=0.2)

    # create 3 nodes (classic Paxos)
    node_ids = [1, 5, 2]
    nodes = {}
    
    for nid in node_ids:
        nodes[nid] = Node(
            node_id=nid,
            network=net,
            peers=node_ids
        )
        net.register(nodes[nid])
        
    visualizer = PaxosVisualizer()
    visualizer.register_nodes(node_ids)
    net.visualizer = visualizer

    # start nodes
    for node in nodes.values():
        asyncio.create_task(node.run())

    # choose node 1 as proposer
    await asyncio.sleep(1)   # let event loop settle
    asyncio.create_task(nodes[2].proposer.propose("VALUE_2")) # node can access proposer class due to Proposer(self) passed to it's self.proposer

    # let Paxos finish
    await asyncio.sleep(5)

await main()
