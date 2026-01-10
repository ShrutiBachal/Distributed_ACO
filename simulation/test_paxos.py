import asyncio
import matplotlib.pyplot as plt

plt.ion()  # interactive mode

from simulation.visualizer import PaxosVisualizer
from core.network import Network
from core.node import Node

async def main():
    net = Network(min_delay=0.1, max_delay=0.5)

    # create 4 nodes (classic Paxos)
    node_ids = [1, 5, 2, 7]
    nodes = {}

    visualizer = PaxosVisualizer()
    visualizer.register_nodes(node_ids)

    net.visualizer = visualizer

    for nid in node_ids:
        nodes[nid] = Node(
            node_id=nid,
            network=net,
            peers=node_ids
        )
        net.register(nodes[nid])

    # start nodes
    for node in nodes.values():
        asyncio.create_task(node.run())

    # choose node 1 as proposer
    await asyncio.sleep(1)   # let event loop settle
    await nodes[1].proposer.propose("VALUE_X")  # node can access proposer class due to Proposer(self) passed to it's self.proposer

    # let Paxos finish
    await asyncio.sleep(3)

await main()
