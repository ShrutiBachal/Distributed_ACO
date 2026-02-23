## Paxos-Based Distributed Line Topology Alignment
### Overview

This project implements a fault-tolerant distributed system that uses the Paxos consensus algorithm to align nodes into a deterministic line topology.

The system demonstrates how consensus can be used as a structural coordination mechanism. Instead of agreeing on a simple value, nodes agree on a global topology structure and then independently compute their positions in the line.

The project emphasizes correctness, modularity, and separation of concerns in distributed systems.

### 📂 Project Structure

The project is organized into three main modules:

    core/
    │   node.py
    │   network.py
    │   message.py

    paxos/
    │   proposer.py
    │   acceptor.py
    │   learner.py

    simulation/
    │   test_paxos.py
    │   visualizer.py
  #### Core Layer

- node.py — Represents each distributed node and maintains local state.

- network.py — Simulates asynchronous message passing.

- message.py — Defines message formats used in Paxos communication.

  #### Paxos Layer

- proposer.py — Handles proposal initiation and majority checking.

- acceptor.py — Manages promise and accept logic.

- learner.py — Learns the chosen consensus value.

  #### Simulation Layer

- test_paxos.py — Runs consensus experiments.

- visualizer.py — Displays the resulting line alignment.

### 🚀 Features

✅ Modular separation of consensus and networking

✅ Fault-tolerant agreement under simulated asynchronous communication

✅ Clean abstraction of Paxos roles

✅ Sequential consensus-driven alignment

✅ Simulated network delays

### ▶️ How to Run
#### 1. Clone the repository
      !git clone https://github.com/ShrutiBachal/Paxos_Simulation
      %cd Paxos_Simulation
        
#### 2. Install Dependencies
      !pip install matplotlib
        
#### 3. Run the Simulation 
      !python simulation/test_paxos.py

### 🔬 Future Enhancements
- Ant Colony Optimization (ACO) for intelligent proposer selection

- Dynamic formation switching

- Real-Time reconfiguration

- 3D formation visualization
