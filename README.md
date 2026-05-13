# Tractor-Trailer Research Project

This repository is organized for development on a notebook, containing the core source code and research documentation for the N-Trailer vehicle kinematics and control project.

## Directory Structure

- `autoware/`: The Autoware autonomous driving stack environment used for simulation and real-world deployment.
- `tracter_ws/`: ROS 2 workspace containing the custom source code and control modules.
  - `src/tracter_control/`: Custom NMPC controller, teleop nodes, and Autoware integration bridge.
  - `src/tracter_trailer/`: Kinematic model, simulation scripts, and visualizers.
  - `src/tracter_odometer/`: Odometer package for tractor-trailer.
- `docs/`: Research documentation and diagrams.
  - `Research/`: KMUTT and TAIST research proposals (Thai/English).
  - `kinematic_diagram_full.png`: Full system kinematic diagram.

## 🚀 Getting Started & Installation

To make setting up the project easy, we use `vcstool` to automatically pull all the necessary sub-repositories defined in `AutoTract.repos`.

### Prerequisites

- Python 3.10+
- ROS 2 (Humble/Foxy)
- `vcstool` (Install via: `sudo apt install python3-vcstool`)

### Workspace Setup (Recommended Workflow)

To fully utilize this project, your environment should be set up in three main phases:

#### 1. Setup Main Project (`AutoTract`)
Start by cloning this root repository, which contains the documentation and workspace structure.
```bash
git clone https://github.com/nontanan-linux/AutoTract.git
cd AutoTract
```

#### 2. Setup Autoware & System Dependencies
The project relies on Autoware for scenario planning and trajectory generation. Before building Autoware, you **must** install essential system dependencies including ROS 2, NVIDIA Drivers, CUDA, and TensorRT.

```bash
# 2.1 Clone Autoware
git clone https://github.com/autowarefoundation/autoware.git
cd autoware

# 2.2 Install System Dependencies (ROS 2, NVIDIA Drivers, CUDA, etc.)
# Note: This script will install all necessary environment tools.
./setup-dev-env.sh -y

# 2.3 Import repositories and Build
vcs import src < autoware.repos
rosdep update
rosdep install -y --from-paths src --ignore-src --rosdistro $ROS_DISTRO
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
cd ../AutoTract
```

#### 3. Setup External Workspace (`tracter_ws`)
Use `vcs` to pull the custom Tracter control packages (our NMPC, Teleop, and Odometer nodes) into the `tracter_ws` workspace.
```bash
# Ensure you are at the root of AutoTract
cd ~/AutoTract

vcs import . < AutoTract.repos
rosdep update
rosdep install -y --from-paths tracter_ws/src --ignore-src --rosdistro $ROS_DISTRO

# Safely clean and build only our custom packages without affecting Autoware
./tracter_build.sh
source install/setup.bash
```

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
