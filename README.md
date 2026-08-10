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

#### 4. Setup CARLA Simulator
To set up the native pre-compiled CARLA Simulator in the workspace folder as defined in `tracter.env` (`~/AutoTract/carla`):

```bash
# Ensure you are at the root of AutoTract
cd ~/AutoTract
mkdir -p carla
```

```bash
# 4.1 Download CARLA 0.9.16 (Verified version) using short URL redirects
wget https://tiny.carla.org/carla-0-9-16-linux -O CARLA_0.9.16.tar.gz
wget https://tiny.carla.org/additional-maps-0-9-16-linux -O AdditionalMaps_0.9.16.tar.gz
```

```bash
# if 0.9.15
wget https://tiny.carla.org/carla-0-9-15-linux -O CARLA_0.9.15.tar.gz
wget https://tiny.carla.org/additional-maps-0-9-15-linux -O AdditionalMaps_0.9.15.tar.gz
```

```bash
# 4.2 Extract packages and import Additional Maps
# Extract main simulator
tar -xzf CARLA_0.9.16.tar.gz -C ~/AutoTract/carla

# Extract Additional Maps directly into the carla directory
tar -xf AdditionalMaps_0.9.16.tar.gz -C ~/AutoTract/carla

# Clean up downloaded archives
rm CARLA_0.9.16.tar.gz AdditionalMaps_0.9.16.tar.gz
```

```bash
# 4.3 Install Python API Client and dependencies
pip install carla==0.9.16 pygame simple-pid
```

### 🗺️ CARLA HDMaps Organization (for Autoware Integration)
To use CARLA maps (Town01-Town07) in Autoware, run the organization script to automatically structure the point cloud and vector maps:
```bash
python3 organize_maps.py
```
This generates organized map folders under `carla/HDMaps/<Town>` containing `pointcloud_map.pcd`, `lanelet2_map.osm`, and `map_projector_info.yaml`.

### Quick Start

#### Option 1: Native Autoware Planning Simulator (No CARLA Required)
Use this option to test Autoware's planning stack locally with a point cloud / Lanelet2 map (e.g. `BG` map):
```bash
source tracter.env
source install/setup.bash

# Run planning simulator with the target map
ros2 launch tracter_launch planning_simulator.launch.xml map_path:=/path/to/autoware_map/BG
```

#### Option 2: CARLA Simulator + Autoware Co-Simulation
Use this option to run Autoware integrated with the CARLA simulator (e.g. `Town01`):

1. **Start CARLA Simulator** (Optimized for laptops with dedicated NVIDIA GPUs):
   ```bash
   cd ~/AutoTract/carla
   __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia ./CarlaUE4.sh -preferNvidia -quality-level=Low -windowed -ResX=800 -ResY=600
   ```

2. **Launch CARLA-Autoware Bridge**:
   ```bash
   cd ~/AutoTract
   source tracter.env
   source install/setup.bash
   ros2 launch carla_autoware_bridge carla_aw_bridge.launch.py town:=Town01 view:=true
   ```
   *(Note: If you run into a CARLA version mismatch error, ensure `CARLA_VERSION` inside the `carla_ros_bridge` package is set to `0.9.16` and rebuild via `colcon build --symlink-install --packages-select carla_ros_bridge`)*

3. **Launch Autoware**:
   ```bash
   cd ~/AutoTract
   source tracter.env
   source install/setup.bash
   ros2 launch tracter_launch e2e_simulator.launch.xml map_path:=/home/tacv/AutoTract/carla/HDMaps/Town01 simulator_type:=carla
   ```


### 🗺️ Resolving Map Coordinate Mismatches (Shifted Map)
If the point cloud map (`PCD`) and the road network (`Lanelet2`) do not align (e.g. they are shifted by 100 km), it is because the point cloud uses a local UTM origin while Autoware defaults to MGRS grid origins.

To fix the alignment for the `BG` map:
1. Open the map projector configuration file: `map_projector_info.yaml` (located in your map directory, e.g. `autoware_map/BG/map_projector_info.yaml`).
2. Change the projector type to `LocalCartesianUTM` and specify the matching UTM origin coordinates:
   ```yaml
   projector_type: LocalCartesianUTM
   vertical_datum: WGS84
   map_origin:
     latitude: 12.662594744072885
     longitude: 99.9208930823293
     altitude: 0.0
   ```
3. Open the coordinate system parameter file: `coordinate_system.param.yaml` in the same directory.
4. Update `coordinate_system` to `4` (LocalCartesianUTM) and configure it with the same origin:
   ```yaml
   /**:
     ros__parameters:
       coordinate_system: 4
       latitude: 12.662594744072885
       longitude: 99.9208930823293
       altitude: 0.0
   ```

For detailed NMPC documentation and execution guides, see [docs/mpc_controller/nmpc.md](docs/mpc_controller/nmpc.md).

To view the research methodology:
Check `docs/Research/Research_Proposal_Thai_Nontanan.md` for the latest structured methodology for NMHE, NMPC, and GWO.

## Development Workflow

1. **Source Code**: All development should happen within `tracter_ws/src`.
2. **Documentation**: Update the `docs/` directory with new findings or model updates.
3. **Simulation**: Use `kinematic_model.py` for model verification and `simulate.py` for visual feedback.
