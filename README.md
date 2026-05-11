# Tractor-Trailer Research Project

This repository is organized for development on a notebook, containing the core source code and research documentation for the N-Trailer vehicle kinematics and control project.

## Directory Structure

- `tracter_ws/`: ROS2-style workspace containing the source code.
  - `src/tracter_trailer/`: Kinematic model, simulation scripts, and visualizers.
  - `src/tracter_odometer/`: Odometer package for tractor-trailer.
- `docs/`: Research documentation and diagrams.
  - `Research/`: KMUTT and TAIST research proposals (Thai/English).
  - `kinematic_diagram_full.png`: Full system kinematic diagram.

## Getting Started

### Prerequisites

- Python 3.10+
- Recommended virtual environment: `.venv` (if already present in source)
- ROS2 (Humble/Foxy) if running node-based simulations.

### Quick Start

To run the kinematic simulation:

```bash
cd tracter_ws/src/tracter_trailer
python3 simulate.py
```

To run the NMPC control simulation (ROS 2):
```bash
source tracter.env
cd docs/mpc_controller/simulation
python3 nmpc_control.py
```

For detailed NMPC documentation and execution guides, see [docs/mpc_controller/nmpc.md](docs/mpc_controller/nmpc.md).

To view the research methodology:
Check `docs/Research/Research_Proposal_Thai_Nontanan.md` for the latest structured methodology for NMHE, NMPC, and GWO.

## Development Workflow

1. **Source Code**: All development should happen within `tracter_ws/src`.
2. **Documentation**: Update the `docs/` directory with new findings or model updates.
3. **Simulation**: Use `kinematic_model.py` for model verification and `simulate.py` for visual feedback.
