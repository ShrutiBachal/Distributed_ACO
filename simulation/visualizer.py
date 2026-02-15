%%writefile simulation/visualizer.py
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from core.message import Message
from core.node import Node

class PaxosVisualizer:
  def __init__(self,network,nodes):
    self.nodes = nodes
    self.network = network
    self.G = nx.DiGraph()
    self.pos = {}
    self.events = deque(maxlen=20)            # recent messages
    self.active_round = set()
    self.p_id = None

    self.colors = {
        "PREPARE": "blue",
        "PROMISE": "green",
        "ACCEPT": "orange",
        "ACCEPTED": "red"
    }
    
  def register_nodes(self, node_ids):
        for n in node_ids:
            self.G.add_node(n)
        for n in self.G.nodes():
            p = self.nodes[n].position
            if p is None or len(p) != 2:    # safety fallback
                p = (0.0, 0.0)
            self.pos[n] = p
    
  def set_active_round(self, proposer_id, round_id):        # used for distinct round visualiztion
    self.active_rounds.add((proposer_id, round_id))         # changed from accepting single active round to accepting multiple active rounds (for multiple proposers)

  def clear_active_round(self, proposer_id, round_id):
    self.active_rounds.discard((proposer_id, round_id))

  def record(self, src, dst, msg_type, proposer_id, round_id, run_id):
    if run_id != self.network.run_id:
        return
    self.events.append({
        "src": src,
        "dst": dst,
        "type": msg_type,
        "proposer": proposer_id,
        "round": round_id
    })
    
  def draw(self):
    plt.clf()
    pos = {}
    for node_id in self.G.nodes():
      pos[node_id] = self.nodes[node_id].position

    if (self.network.consensus_reached):    
        t = (self.network.end_time - self.network.start_time)    # Displaying total time taken for single consensus 
        if t is not None:
          plt.text(
            0.5, -0.15,
            f"Consensus Time: {t:.4f} seconds",
            fontsize=11,
            color="black",
            ha="center",
            transform=plt.gca().transAxes
          )
          
    # draw nodes
    nx.draw_networkx_nodes(
        self.G,
        pos,
        node_size=500,
        node_color="lightblue"
    )
    nx.draw_networkx_labels(self.G, pos,font_size=10)

    for event in self.events:
        src = event["src"]
        dst = event["dst"]
        msg_type = event["type"]
        proposer = event["proposer"]
        round_id = event["round"]

        is_active = (proposer, round_id) == self.active_round
        base_color = self.colors.get(msg_type, "black")

        if is_active:
            color = base_color
            width = 2.5
            alpha = 1.0
        else:
            color = "lightgrey"              # color fading if not the current round
            width = 1.0
            alpha = 0.4
          
        # draw edges
        nx.draw_networkx_edges(
            self.G,
            pos,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
            edgelist=[(src, dst)],
            edge_color = color,               # your color list
            width=width,
            alpha=alpha,
            connectionstyle="arc3,rad=0.1"
        )

        # label
        label = f"P{proposer}-R{round_id}-{msg_type}"    # labeling the path with Proposer_id and round_id instead of Message type
        nx.draw_networkx_edge_labels(
            self.G,
            pos,
            edge_labels={(src, dst): label},
            font_color=color,
            font_size=9,
            label_pos=0.5
        )

    plt.title("Paxos Message Flow")
    plt.axis("off")
    plt.pause(0.005)
