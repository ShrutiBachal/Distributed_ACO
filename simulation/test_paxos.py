import asyncio
import matplotlib.pyplot as plt

plt.ion()  # interactive mode

from uuid import uuid4
from simulation.visualizer import PaxosVisualizer
from core.network import Network
from core.node import Node
from paxos.learner import Learner

async def main():
    run_id = str(uuid4())
    net = Network(min_delay=0.05, max_delay=0.2)
    net.run_id = run_id

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
        learner = Learner(nodes[nid])
        
    # start nodes
    for node in nodes.values():
        asyncio.create_task(node.run())
        
    visualizer = PaxosVisualizer()
    visualizer.register_nodes(node_ids)
    net.visualizer = visualizer
    await asyncio.sleep(1)

    for node in node_ids:
        value = {
            "robot_id": node,
            "target": Node.line_target(node, 2.0)
        }
        asyncio.create_task(nodes[node].proposer.propose(value))

        await asyncio.sleep(8)
        visualizer.draw()

    if(learner.learned_value != None):
          if not net.consensus_reached:
              net.consensus_reached = True
              print(f"[CONSENSUS] reached in {duration:.4f}s")
    net.end_run(success = True)       # 2
    duration = net.end_time - net.start_time  # made out of if block

await main()
