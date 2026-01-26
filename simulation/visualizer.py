%%writefile simulation/visualizer.py
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

class PaxosVisualizer:
  def __init__(self,network):
    self.network = network
    self.G = nx.DiGraph()
    self.events = deque(maxlen=20)            # recent messages
    self.pos = nx.spring_layout(self.G)
    self.active_round = None
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
        self.pos = nx.circular_layout(self.G)
    
  def set_active_round(self, proposer_id, round_id):          # used for distinct round visualiztion
    self.active_round = (proposer_id, round_id)

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

  def learned(self, node_id, value):
      plt.text(
        0.5, -0.1,
        f"LEARNED VALUE = {value} at Node {node_id} in time : {self.network.end_time - self.network.start_time}",
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
        self.G, self.pos,
        node_size=500,
        node_color="lightblue"
    )
    nx.draw_networkx_labels(self.G, self.pos,font_size=10)

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
            self.pos,
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
        label = f"P{proposer}-R{round_id}"    # labeling the path with Proposer_id and round_id instead of Message type
        nx.draw_networkx_edge_labels(
            self.G,
            self.pos,
            edge_labels={(src, dst): label},
            font_color=color,
            font_size=9,
            label_pos=0.5
        )

    plt.title("Paxos Message Flow")
    plt.axis("off")
    plt.pause(0.005)
