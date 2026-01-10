%%writefile simulation/visualizer.py
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

class PaxosVisualizer:
  def __init__(self):
    self.G = nx.DiGraph()
    self.events = deque(maxlen=20)  # recent messages
    self.pos = nx.spring_layout(self.G)

    self.colors = {
        "PREPARE": "blue",
        "PROMISE": "green",
        "ACCEPT": "orange",
        "ACCEPTED": "red"
    }

  def register_nodes(self, node_ids):
        for n in node_ids:
            self.G.add_node(n)
        self.pos = nx.circular_layout(self.G)

  def record(self, src, dst, msg_type):
        self.events.append((src, dst, msg_type))

  def learned(self, node_id, value):
      plt.text(
        0.5, -0.1,
        f"LEARNED VALUE = {value} at Node {node_id}",
        fontsize=12,
        color="purple",
        ha="center",
        transform=plt.gca().transAxes
      )
      nx.draw_networkx_nodes(
        self.G,
        self.pos,
        nodelist=[node_id],
        node_color="violet",
        node_size=1600
      )
    
  def draw(self):
    plt.clf()
    ax = plt.gca()

    # draw nodes
    nx.draw_networkx_nodes(
        self.G, self.pos,
        node_size=500,
        node_color="lightblue"
    )
    nx.draw_networkx_labels(self.G, self.pos,font_size=10)

    for src, dst, msg_type in self.events:
        color = self.colors.get(msg_type, "black")

        # draw edges
        nx.draw_networkx_edges(
            self.G,
            self.pos,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
            edgelist=[(src, dst)],
            edge_color = color,   # your color list
            width=2,
            connectionstyle="arc3,rad=0.1"
        )

        # label
        nx.draw_networkx_edge_labels(
            self.G,
            self.pos,
            edge_labels={(src, dst): msg_type},
            font_color=color,
            font_size=9,
            label_pos=0.5
        )

    plt.title("Paxos Message Flow")
    plt.axis("off")
    plt.pause(0.004)
