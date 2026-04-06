# Research Proposal: Path Tracking for Multi-Trailer Tow Truck

**Title**: Development of an Adaptive Path Tracking Control System for a Multi-Trailer Autonomous Tow Truck using Metaheuristic Optimization in CARLA Simulator

**Student Name**: Nontanan Sommat

**Program**: Dept. of Automotive Engineering (A2TE), TAIST-Tokyo Tech

**University**: King Mongkut's University of Technology Thonburi (KMUTT)

**Advisor**: Asst. Prof. Dr. Danai Phaoharuhansa

---

## 1. Abstract

The operation of multi-trailer autonomous tow trucks (Standard N-Trailer systems) presents significant control challenges due to non-holonomic kinematic constraints, off-tracking effects, and potential instabilities like jackknifing. Furthermore, real-world uncertainty, specifically steering bias and mechanical wear, can significantly degrade tracking accuracy. This research proposes an adaptive control framework that integrates Nonlinear Model Predictive Control (NMPC) with Nonlinear Moving Horizon Estimation (NMHE) for robust state and bias compensation. Additionally, a Grey Wolf Optimizer (GWO) is utilized for optimal weight tuning of the controller's cost function. The system is validated using high-fidelity simulations in the CARLA Simulator integrated with ROS 2 and Autoware Universe.

## 1. INTRODUCTION

### 1.1 Introduction and Background

The rapid growth of intelligent transportation and autonomous logistics has made Autonomous Vehicles (AVs) a critical technology for increasing efficiency and reducing accidents. However, the operation of Articulated Vehicles or Multi-Trailer Systems, particularly those with multiple drawbar trailers (such as a tractor with four trailers), remains a high-level engineering challenge. These systems are characterized by highly complex non-linear dynamics, recursive kinematic structures, and inherent instabilities such as jackknifing and significant off-tracking behavior during cornering.

A key hurdle in autonomous trailer control is achieving precise path tracking under external disturbances and parameter uncertainties, such as steering bias or variable mechanical friction. Traditional controllers often fail to handle physical constraints comprehensively. This research proposes the integration of Nonlinear Model Predictive Control (NMPC), which enables proactive behavior prediction and direct constraint handling, with Nonlinear Moving Horizon Estimation (NMHE) for deep state and bias compensation. Furthermore, Grey Wolf Optimization (GWO) is utilized for optimal weight tuning to ensure maximum robustness and safety.

### 1.2 Objective of the Research

1) To design and develop a Nonlinear Model Predictive Control (NMPC) system using a Full-Kinematic Model for a tractor with four drawbar trailers to achieve high-precision path tracking.
2) To develop a state and bias estimation system using NMHE for adaptive compensation of external disturbances and steering inaccuracies.
3) To utilize the Grey Wolf Optimization (GWO) algorithm for optimal weight tuning (Optimal Weight Tuning) of the NMPC cost function.
4) To evaluate and compare the performance of the proposed system against basic baseline controllers within the ROS2 architecture and CARLA Simulator.

### 1.3 Scope and Limitation of the Study

1) **Vehicle Configuration**: Focuses on a tractor and four drawbar trailers (Tractor-Drawbar Trailer configuration).
2) **Modeling Scope**: Primarily utilizes a Kinematic Model for controller design, considering physical constraints such as steering angles and articulation angles for jackknifing prevention.
3) **Software Scope**: Developed on ROS2 (Humble/Foxy) using CARLA Simulator (v0.9.15) integrated with Autoware Universe.
4) **Testing Scenarios**: Includes Path Tracking, Lane Change, and Robustness Tests (e.g., against steering bias).
5) **Limitations**: This research focuses on Software-in-the-Loop (SiL) testing and does not currently cover real-world road testing.

### 1.4 Expected Benefits

1) A high-precision motion control system for autonomous trailers capable of effective jackknifing prevention.
2) A robust methodology for state and bias estimation (NMHE) applicable to complex systems with limited sensors or high disturbances.
3) Reduced time and resources for MPC parameter tuning through the use of metaheuristic optimization (GWO).
4) Knowledge that can be applied to autonomous freight industries to enhance safety and spatial efficiency in warehouses and on public roads.

## 2. LITERATURE REVIEWS

This chapter discusses a review of the literature and related research used in the research, including:

### 2.1 Literature related to kinematics and control of multi-trailer articulated vehicles

The control of multi-trailer articulated vehicles (MTAVs), often referred to as "Standard N-Trailer" systems, is a well-studied yet challenging domain. The research titled "**Path tracking control of automated vehicles based on adaptive MPC in variable conditions**" by **Liu et al. (2024)** and others emphasizes that these systems are subject to non-holonomic constraints and recursive kinematic dependencies. The primary challenges include "off-tracking," where the trailers do not follow the path of the lead vehicle precisely, and "jackknifing," an unstable state where the articulation angle exceeds safety limits. This study utilizes a recursive kinematic formulation to model a tractor with four trailers, specifically addressing off-axle hitching geometry ($d_h$) which significantly influences the system's maneuverability.

#### 2.1.1 A Universal and Reconfigurable Stability Control Methodology for Articulated Vehicles With Any Configurations (Zhang et al., 2020)

##### 2.1.1.1 Background & Significance

This research proposes a "Universal and Reconfigurable" control architecture methodology for all types of articulated vehicles. It addresses the diversity of truck configurations in the transportation industry, which often have varying numbers of trailers and wheel positions, leading to a high center of gravity (CG) and risks of severe accidents such as Jackknifing or Trailer Sway. The researchers developed a "unified model and controller" applicable to any configuration by simply adjusting Boolean configuration matrices, eliminating the need to redesign controllers for each specific trailer type.

##### 2.1.1.2 Objectives & Scope

- **Primary Goal**: Develop an Integrated Stability Control system that manages yaw stability, lateral stability, and roll stability through the concept of Virtual Corrective C.G. Forces.
- **Key Assumptions and Scope**:
  - Utilizes a **Linearized Brush Tire Model** via Taylor expansion to linearize tire friction into an affine model within the operating range.
  - Assumes a **small articulation angle ($\lambda$)** during operation to allow for the linearization of kinematics at the hitch point.
  - Assumes that vehicle dimensions (wheelbase, mass) and actuator configurations are known and remain constant during operation.

##### 2.1.1.3 Methodology

The control architecture is divided into two hierarchical layers based on **Figure 3 (A complete structure of controller)**:

- **Reconfigurable Vehicle Model**: A state-space equation covering all vehicle types is defined using an **Axle Boolean Matrix ($T_c$)** and an **Actuator Boolean Matrix ($T_w$)**. These matrices specify the active axles and wheels. The equation of motion for the tractor-trailer system with hitching is defined as (Ref. Eq. 22):
  $$ \dot{x} = (A+CJ K_1)x + (B-CJ K_2)F_{CG} $$
  where $x = [v_x, v_y, r, \phi, \dot{\phi}]^T$ is the state vector and $F_{CG} = [\Delta F_x, \Delta F_y, \Delta M_z]^T$ represents the corrective forces and moments at the C.G.
  
- **High-Level Controller (MPC)**: A **Linear Time-Varying MPC** computes the predictive corrective vector $v^*$ to maintain stability. The optimization problem over the prediction horizon ($N_p$) is defined by the cost function (Ref. Eq. 26):
  $$ J = \sum_{k=1}^{N_p} \| y_{t+k|t} - y_{d,t+k|t} \|_{Q}^2 + \sum_{k=0}^{N_c-1} \left( \| v_{t+k|t} \|_{R}^2 + \| \Delta v_{t+k|t} \|_{S}^2 \right) $$
  focusing on State Tracking ($Q$), minimizing Control Effort ($R$), and preventing oscillations via Slew Rate ($S$) constraints.

- **Lower-Level Controller (Control Allocation - CA)**: Distributes the corrective forces $v^*$ from the MPC to individual actuators (Ref. Eq. 29 and 30) using the **Control effectiveness matrix** $B_p = L_c T_c L_w T_w B_1$. The optimization problem (Eq. 30):
  $$ \min_{u} \; \xi \| v^* - B_p u \|_{W_e}^2 + \| u \|_{W_u}^2 \quad s.t. \quad l_b \le u \le u_b $$
  allows the system to automatically handle actuator failures within physical limits.

##### 2.1.1.4 Key Results

- **Rollover Prevention**: In severe Double Lane Change tests, the controller **reduced the Rollover Index (RI) by 36.5%** (from 0.82 to a safe level of 0.52) (Ref. Figure 10).
- **Anti-Jackknifing**: In low-mu braking scenarios with steering, the uncontrolled vehicle jackknifes beyond 90 degrees. With the MPC-CA system active, the **articulation angle was stably saturated at approximately 10 degrees** (Ref. Figure 11).

#### 2.1.2 Research on Path-Tracking Control of Articulated Vehicle with a trailer Based on Advanced Model Prediction Control Strategy (Liu et al., 2021)

##### 2.1.2.1 Background & Significance

This research proposes an advanced path-tracking strategy for Articulated Heavy Vehicles (AHVs) to enhance path-following accuracy and road adaptability. The methodology integrates **Model Predictive Control (MPC)**, designed for minimizing lateral tracking errors during curve negotiation, with **Optimal Curvature Preview Control (OCPC)**, which focuses on maintaining driving stability during straight-line operation. This hybrid approach effectively addresses the limitations of traditional controllers, particularly the significant tracking errors typically encountered during the transition between straight segments and curves.

##### 2.1.2.2 Objectives & Scope

- **Primary Goal**: Develop a coordinated controller that combines the predictive benefits of MPC with the stability of OCPC to improve the tracking performance of single-trailer articulated vehicles.
- **Scope and Focus**:
  - Utilizes a **3-DOF Single Track Yaw-Plane Model** to represent the lateral and yaw dynamics of both the tractor and trailer.
  - Employs a **co-simulation platform** using TruckSim and MATLAB/Simulink for validation.
  - Focuses on medium and high-speed operations where dynamic constraints (mass, inertia, tire slip) become critical, necessitating a dynamics-based model over simple kinematics.

##### 2.1.2.3 Methodology

The control framework is structured around a switching logic that selects the optimal controller based on road geometry:

- **Vehicle Dynamics Modeling**: Defines equations for lateral and yaw motion, linearized tire dynamics, and articulation constraints.
- **MPC Layer (Curve Negotiation)**: Formulates an optimization problem using discrete state-space equations to minimize lateral error and yaw deviation over a prediction horizon ($N_p$), subject to actuator limits and stability constraints.
- **OCPC Layer (Straight-Line Stability)**: Applies an optimal preview technique based on the Ackerman steering principle and preview time ($T_p$) adjustment, ensuring the vehicle remains centered and stable at higher speeds.

##### 2.1.2.4 Key Results

- **Error Reduction**: In Double Lane Change tests at 30 km/h, the MPC+OCPC controller **reduced the maximum lateral tracking error by 14 cm** (from 17 cm to 3 cm) compared to MacAdam’s optimal preview controller.
- **High-Speed Stability**: At 100 km/h (Single Lane Change), the system maintained a **Rearward Amplification (RWA) index below 1.0** (specifically 0.83 for lateral acceleration), whereas traditional controllers exhibited unstable RWA values exceeding 1.17, leading to a significant improvement in lateral stability.

### 2.2 Literature related to nonlinear model predictive control (NMPC) and moving horizon estimation (NMHE)

Model Predictive Control (MPC) has emerged as a state-of-the-art solution for autonomous vehicle control due to its ability to incorporate physical constraints directly into the optimization problem. **Lin et al. (2019)** demonstrated that adaptive MPC can significantly improve tracking accuracy under variable road conditions. To complement the controller, Moving Horizon Estimation (MHE) is used for state and parameter observation. **NMHE** extends this by handling non-linear system dynamics, allowing for the real-time estimation of "steering bias" or other physical uncertainties. Integrating NMPC and NMHE creates a robust "Moving Horizon" control framework suitable for high-degree-of-freedom systems like multi-trailer tow trucks.

#### 2.2.1 Experimental Validation of Linear and Nonlinear MPC on an Articulated Unmanned Ground Vehicle (Kayacan et al., 2018)

##### 2.2.1.1 Background & Significance

Efficient trajectory tracking for articulated vehicles remains a challenge due to their non-linear dynamics and susceptibility to varying ground conditions. This research addresses the computational trade-off between **Nonlinear Model Predictive Control (NMPC)** and **Linear Model Predictive Control (LMPC)** using input-state linearization. It highlights the importance of combining NMPC with **Nonlinear Moving Horizon Estimation (NMHE)** to handle model uncertainties and parameter variations in real-time, which is a critical bridge between theoretical control and practical deployment on autonomous agricultural platforms.

##### 2.2.1.2 Objectives & Scope

- **Primary Goal**: Compare the trajectory tracking performance and computational cost of an NMHE-NMPC framework against a traditional Input-State Linearization with LMPC (ISL-LMPC) framework.
- **Scope**:
  - Validated on a small-scale articulated unmanned tractor-trailer system.
  - Focuses on time-based trajectory tracking (8-shaped paths) involving both straight and curvilinear segments.
  - Considers online estimation of traction parameters (longitudinal and side slips).

##### 2.2.1.3 Methodology

- **NMHE-NMPC Framework**:
  - **NMHE**: Used to estimate unmeasurable states and time-varying traction parameters ($\mu, \kappa, \eta$) online, addressing uncertainties caused by varying soil conditions.
  - **NMPC**: Formulated using a fast real-time iteration scheme based on the Gauss-Newton method and multiple shooting to minimize feedback delay.
- **ISL-LMPC Framework**:
  - Transforms the non-linear tractor-trailer model into a virtual linear model using Input-State Linearization.
  - Applies a standard LMPC to the linearized system for computational efficiency.
- **Tools**: Implemented using **ACADO Toolkit** for code generation and **qpOASES** as the QP solver.

##### 2.2.1.4 Key Results

- **Tracking Performance**: The NMHE-NMPC framework outperformed ISL-LMPC in all scenarios. For curvilinear segments, NMPC reduced tracking errors significantly, while ISL-LMPC results were comparable but slightly degraded due to the linearization assumptions.
- **Computational Efficiency**: While LMPC was approximately 8 times faster (~1.2 ms), the NMPC framework achieved a total execution time of ~12 ms (including NMHE), proving that advanced non-linear control is feasible for real-time mobile robotics with modern optimization solvers.
- **Adaptability**: NMHE successfully identified changing traction parameters online, allowing the NMPC to maintain high precision even in uneven and varying terrain.

#### 2.2.2 Real-Time Longitudinal and Lateral State Estimation of Preceding Vehicle Based on Moving Horizon Estimation (Liu et al., 2021)

##### 2.2.2.1 Background & Significance

Accurate state estimation of surrounding vehicles is a prerequisite for reliable autonomous driving functions such as Adaptive Cruise Control (ACC) and Autonomous Emergency Braking (AEB). While Extended Kalman Filters (EKF) are commonly used, they often struggle with the highly non-linear nature of vehicle kinematics and the explicit handling of physical constraints. This research highlights the advantages of **Moving Horizon Estimation (MHE)** as an optimization-based alternative that can explicitly incorporate state constraints and non-linear models over a sliding window of past data, providing superior robustness in complex urban and highway scenarios.

##### 2.2.2.2 Objectives & Scope

- **Primary Goal**: Develop a modular, real-time estimation framework capable of accurately observing both the longitudinal and lateral states of a preceding vehicle.
- **Scope**:
  - Focuses on "preceding vehicle" tracking using sensor data (LiDAR/Radar).
  - Handles non-linear vehicle kinematic models.
  - Prioritizes real-time computational feasibility for onboard deployment.

##### 2.2.2.3 Methodology

- **Modular Estimation Architecture**:
  - **Longitudinal Estimator**: Uses a **Linear MHE** to estimate longitudinal velocity and acceleration. Since the longitudinal kinematics are relatively linear, this ensures high speed without sacrificing accuracy.
  - **Lateral Estimator**: Employs a **Nonlinear MHE (NMHE)** to handle the non-linear relationship between heading angle, yaw rate, and lateral position.
- **Real-Time Optimization (Multiple Shooting)**:
  - To address the computational intensive nature of NMHE, the authors utilize the **Multiple Shooting (MS)** method. This technique discretizes the estimation horizon into smaller segments, allowing for parallelizable computation and faster convergence compared to single shooting methods.
- **Constraints**: Explicitly incorporates physical boundaries such as maximum acceleration/deceleration and steering limits into the MHE cost function.

##### 2.2.2.4 Key Results

- **Estimation Accuracy**: Compared to standard EKF, the MHE-based approach reduced root-mean-square error (RMSE) in heading angle and lateral position estimation by over **20%** during aggressive lane-changing maneuvers.
- **Computational Performance**: By leveraging the modular structure and Multiple Shooting, the total execution time was maintained within **15 ms**, making it suitable for high-frequency control loops (e.g., 50-100 Hz).
- **Robustness**: The system demonstrated high resilience against measurement outliers and sensor noise, a critical factor for the safety of autonomous trajectory following.

### 2.3 Literature related to meta-heuristic optimization and parameter tuning using Grey Wolf Optimizer (GWO)

Metaheuristic algorithms are frequently used to solve complex optimization problems where traditional gradient-based methods may fail. The **Grey Wolf Optimizer (GWO)**, inspired by the social hierarchy and hunting behavior of grey wolves, is noted for its balance between exploration and exploitation. In the context of NMPC, GWO is particularly effective for **Optimal Weight Tuning**. Tuning the weighting matrices ($Q$ and $R$) is often a manual and time-consuming process; GWO automates this by searching for the parameter set that minimizes tracking error and control effort across diversascenarios.

#### 2.3.1 Design a New Hybrid Controller Based on an Improvement Version of Grey Wolf Optimization for Trajectory Tracking of Wheeled Mobile Robot (Hussein, 2023)

##### 2.3.1.1 Background & Significance

Nonholonomic wheeled mobile robots (WMRs) are widely used in hazardous environments, such as mining and explosive detection, where precise trajectory tracking is essential. However, finding the optimal control gains for such multi-input multi-output (MIMO) systems is challenging due to their nonlinear dynamics. This research demonstrates the effectiveness of the **Grey Wolf Optimizer (GWO)** in automating the parameter tuning process for hybrid control systems, ensuring robust performance under varying trajectories (e.g., S-shaped paths) and reducing the dependency on trial-and-error manual tuning.

##### 2.3.1.2 Objectives & Scope

- **Primary Goal**: Design and optimize a hybrid control architecture for a nonholonomic wheeled mobile robot to achieve high-precision trajectory tracking.
- **Scope**:
  - Targets a two-driving-wheel robot with a caster wheel.
  - Implements a hybrid control scheme: Kinematic-based (Fractional order PID) and Dynamic-based (LQR).
  - Validates performance using S-shaped trajectories in a MATLAB simulation environment.

##### 2.3.1.3 Methodology

- **Hybrid Control Architecture**:
  - **Fractional Order PID (FOPID)**: Used to control the robot's linear and angular velocities based on the kinematic model. FOPID offers more degrees of freedom than standard PID through fractional integral and derivative orders.
  - **Linear Quadratic Regulator (LQR)**: Applied to the dynamic model to control the motor torques, ensuring optimal state-space performance.
- **Improved Grey Wolf Optimization (IGWO)**:
  - An **Improved GWO** algorithm is used to simultaneously tune **11 parameters**: five for the FOPID controller (Kp, Ki, Kd, $\alpha$, $\beta$) and six for the LQR weighting matrices ($Q$ and $R$).
  - The "Improvement" focuses on balancing exploitation and exploration by introducing an adaptive convergence factor, which prevents the optimization from getting trapped in local minima and ensures rapid convergence.

##### 2.3.1.4 Key Results

- **Tracking Precision**: The optimized hybrid controller achieved extremely low Mean Square Error (MSE) in X and Y coordinates (down to $10^{-4}$ and $10^{-5}$ meters respectively), significantly outperforming non-optimized and traditional PID controllers.
- **Control Smoothness**: Unlike heuristic tuning, the GWO-tuned controller generated smooth control input signals without sharp spikes, which is critical for protecting the physical actuators and ensuring vehicle longevity.
- **Robustness**: The IGWO demonstrated superior reliability in finding the global optimum across complex path segments, proving its utility for "Adaptive" control frameworks in autonomous robotics.

#### 2.3.2 A Prognosis Technique Based on Improved GWO-NMPC to Improve the Trajectory Tracking Control System Reliability of Unmanned Underwater Vehicles (Gan et al., 2023)

##### 2.3.2.1 Background & Significance

Unmanned Underwater Vehicles (UUVs) operate in highly nonlinear and uncertain marine environments, making trajectory tracking a complex control problem. Traditional optimization methods for Nonlinear Model Predictive Control (NMPC), such as Sequential Quadratic Programming (SQP), can be computationally expensive and sensitive to initial conditions. This research proposes the integration of an **Improved Grey Wolf Optimizer (IGWO)** as the core solver for NMPC, aiming to enhance the reliability and real-time performance of trajectory tracking systems by leveraging the global search capabilities of metaheuristic algorithms.

##### 2.3.2.2 Objectives & Scope

- **Primary Goal**: Improve the tracking accuracy and reliability of UUVs by optimizing the NMPC control law using an improved metaheuristic approach.
- **Scope**:
  - Focuses on a three-degree-of-freedom (3-DOF) horizontal model of a UUV.
  - Implements the controller within a **Robot Operating System (ROS)** simulation environment.
  - Conducts comparative analysis between IGWO, standard GWO, and traditional SQP algorithms.

##### 2.3.2.3 Methodology

- **Improved GWO (IGWO) Design**:
  - **Nonlinear Convergence Factor**: Replaces the linear decay of the convergence factor with a nonlinear attenuation function. This allows for more time in the exploration phase and a faster transition to the exploitation phase, improving the algorithm's search efficiency.
  - **Memory Function**: Adds a memory mechanism to the position update equation, allowing wolves to retain information from previous iterations, which prevents the optimization from oscillating and speeds up convergence.
- **GWO-NMPC Framework**:
  - The IGWO is used as the **rolling optimization solver** to minimize the cost function at each sampling step. The cost function penalizes both the pose error (relative to the reference trajectory) and the control increment to ensure smooth operation.
- **Simulation Platform**: Validated using the UUV simulator in ROS, which incorporates realistic hydrodynamic and environmental disturbances.

##### 2.3.2.4 Key Results

- **Superior Convergence**: Compared to traditional SQP and standard GWO, the IGWO-NMPC framework achieved a **faster convergence rate** in tracking error, particularly when dealing with complex or substantial changes in the reference trajectory.
- **Enhanced Reliability**: The inclusion of the memory function and nonlinear factor significantly reduced the risk of falling into local optima, ensuring that the controller consistently found a near-global optimal solution for the control inputs.
- **Real-Time Feasibility**: The research demonstrated that the IGWO effectively balanced search accuracy with computational speed, making it a viable alternative for the online optimization required in high-stakes autonomous vehicle operations.

### 2.4 Simulation and System Integration using ROS2, Autoware, and CARLA

The complexity of multi-trailer autonomous systems necessitates a high-fidelity simulation environment for validation before real-world deployment. This section reviews research focused on the architectural integration of autonomous driving stacks with realistic simulators.

#### 2.4.1 CARLA-Autoware-Bridge: Facilitating Autonomous Driving Research with a Unified Framework for Simulation and Module Development (Kaljavesi et al., 2024)

##### 2.4.1.1 Background & Significance

System-level testing of autonomous driving (AD) modules requires seamless compatibility between the software stack and the simulation environment. This research addresses the challenges of bridging **Autoware Core/Universe** (the state-of-the-art ROS 2-based stack) with the **CARLA Simulator**. The significance of this work lies in providing a unified, decoupled framework that allows researchers to evaluate high-level AD modules (like NMPC path tracking) in a safe, reproducible, and physically accurate virtual environment without the overhead of low-level hardware interfacing.

##### 2.4.1.2 Objectives & Scope

- **Primary Goal**: Develop and analyze an efficient bridge connecting CARLA with Autoware Universe to facilitate modular research.
- **Scope**:
  - Utilizes **ROS 2** as the communication middleware.
  - Supports high-fidelity sensor models (LiDAR, Cameras, IMU, GNSS).
  - Evaluates the bridge's performance in terms of communication latency and control fidelity.

##### 2.4.1.3 Methodology

- **Unified Bridge Architecture**:
  - The framework separates the Simulator (CARLA), the Middleware (ROS-Bridge), and the AV Stack (Autoware). This modularity allows for independent updates to any component.
  - **Sensor Data Mapping**: Optimizes the conversion of CARLA's raw data (e.g., dense LiDAR point clouds) into ROS 2 standard messages (e.g., `sensor_msgs/PointCloud2`) compatible with Autoware's perception layer.
- **Control Interface**:
  - **Ackermann Command Translation**: Converts Autoware’s target steering angle and velocity into CARLA’s vehicle control signals (Throttle, Brake, Steering).
  - **Longitudinal Control**: Implements a dedicated PID-based velocity controller within the bridge to accurately track target speeds, compensating for the physical inertia of vehicles in the CARLA environment.
- **Latency Analysis**: Conducts rigorous testing to measure the "End-to-End" latency from sensor perception in CARLA to control command execution, ensuring that the system is suitable for high-speed or safety-critical maneuvers.

##### 2.4.1.4 Key Results

- **High-Fidelity Integration**: Successfully demonstrated a complete loop where Autoware processes CARLA's sensor data and sends back control commands that accurately drive the ego-vehicle.
- **Real-Time Performance**: The latency analysis indicated an average processing time of approximately **7.8ms** for a standard sensor kit, which is well within the requirements for real-time autonomous driving control (typically targeting <100ms total latency).
- **Research Utility**: The bridge facilitates "Software-in-the-Loop" (SiL) testing, allowing complex models like the multi-trailer kinematic system to be validated against realistic tire physics and LIDAR-based localization provided by CARLA.

#### 2.4.2 Event-Triggered Model Predictive Control for Autonomous Vehicle Path Tracking: Validation Using CARLA Simulator (Zhou et al., 2023)

##### 2.4.2.1 Background & Significance

While Nonlinear Model Predictive Control (NMPC) is powerful for path tracking, its real-world application is often limited by the high computational requirement of solving the optimization problem in real-time. This research addresses this bottleneck by proposing an **Event-Triggered MPC framework**. The significance of this study lies in its validation within the **CARLA Simulator**, demonstrating that computational load can be significantly reduced without compromising the safety and accuracy of high-fidelity autonomous driving.

##### 2.4.2.2 Objectives & Scope

- **Primary Goal**: Develop and validate an event-triggered mechanism that reduces the number of optimization problems solved during autonomous navigation.
- **Scope**:
  - Focuses on lateral path tracking control (Steering).
  - Utilizes a bicycle vehicle dynamic model with parameter estimation.
  - Validated using **CARLA 0.9.13** in complex urban driving scenarios.

##### 2.4.2.3 Methodology

- **Event-Triggering Mechanism**:
  - Unlike traditional time-triggered MPC that solves the OCP periodically, this method only triggers a new optimization solve if:
    1. The **lateral offset ($d_y$)** exceeds a pre-defined threshold ($\sigma$).
    2. The previously optimized control sequence is depleted (time limit $k > k_{max}$).
  - In other states, the controller reused the previously computed optimal control sequence, effectively skipping costly optimization steps.
- **Offline Parameter Estimation with Genetic Algorithm (GA)**:
  - This is a critical step for simulation fidelity. The researchers used a **Genetic Algorithm** to estimate vehicle parameters (e.g., cornering stiffness, moment of inertia) to ensure the simplified bicycle model used in the MPC prediction matches the high-fidelity physics of CARLA.
- **Path Smoothing**: Employed **Bezier curves** for lane-change maneuvers to ensure a continuous and differentiable reference trajectory for the controller.

##### 2.4.2.4 Key Results

- **Computational Reduction**: The results demonstrated a significant reduction in the frequency of MPC triggering (solving fewer OCPs) while maintaining acceptable path tracking performance.
- **Accuracy vs. Efficiency**: The study provides a clear trade-off analysis between the trigger threshold ($\sigma$) and tracking error, showing that for thresholds like $\sigma = 0.02m$, the computational burden decreased by over **80%** with negligible impact on RMS error.
- **Real-Time Feasibility**: By reducing the CPU load, the event-triggered approach makes NMPC a viable option for deployment on edge computing hardware typically found in autonomous vehicles.

## 3. METHODOLOGY

This chapter details the research methodology employed to develop the adaptive path-tracking control system for the multi-trailer tow truck. The structure has been streamlined to ensure modularity and reduce redundancy as follows:

### 3.1 Simulation Environment and Digital Twin Construction

This research is conducted using the CARLA Simulator (v0.9.15), focusing on creating a high-fidelity digital twin of the operative environment:

- **Vehicle Kinematics**: The configuration of the tractor with four drawbar trailers is defined as follows:

![Kinematic Diagram](kinematic_diagram_full.png)

#### 1. System Description

The system consists of a tractor followed by $N=4$ trailer units. Each unit is composed of a drawbar and a trailer body, connected in a serial chain configuration.

#### 2. System Kinematics Vector

The state of the system is defined by the kinematic vector $\mathbf{q}_{kin}$ comprising $3 + 2N$ variables:
$$ \mathbf{q}_{kin} = [x_0, y_0, \theta_0, \underbrace{\theta_1, \theta_2}_{\text{Trailer 1}}, \dots, \underbrace{\theta_{2N-1}, \theta_{2N}}_{\text{Trailer N}}]^T $$
where $x_0, y_0, \theta_0$ represent the tractor's pose, $\theta_{2i-1}$ is the $i$-th drawbar angle, and $\theta_{2i}$ is the $i$-th trailer body angle.

#### 3. System Parameters

| Parameter | Symbol | Description |
| :--- | :--- | :--- |
| **Tractor** | $L_0$ | Wheelbase |
| | $d_h$ | Hitch offset behind the rear axle |
| **Trailer $i$** | $L_{bar,i}$ | Drawbar length |
| | $L_{trl,i}$ | Trailer length (dolly to axle) |
| | $d_{h,i}$ | Hitch offset of trailer $i$ (for consecutive hitching) |

#### 4. Mathematical Model

Derived assuming no-slip conditions for all wheels:

##### 4.1 Tractor Kinematics

$$ \dot{x}_0 = v_0 \cos\theta_0, \quad \dot{y}_0 = v_0 \sin\theta_0, \quad \dot{\theta}_0 = \frac{v_0}{L_0} \tan\delta $$

##### 4.2 Trailer 1 Kinematics

$$ \dot{\theta}_1 = \frac{1}{L_1} \left( v_0 \sin(\theta_0 - \theta_1) - d_h \dot{\theta}_0 \cos(\theta_0 - \theta_1) \right) $$
$$ v_1 = v_0 \cos(\theta_0 - \theta_1) + d_h \dot{\theta}_0 \sin(\theta_0 - \theta_1) $$
$$ \dot{\theta}_2 = \frac{v_1}{L_2} \sin(\theta_1 - \theta_2), \quad v_2 = v_1 \cos(\theta_1 - \theta_2) $$

##### 4.3 - 4.5 Trailer 2, 3, and 4 Kinematics

Following the same logic, the motion is propagated via the hitch velocity of the preceding unit.

#### 5. Matrix Form

To support $N$ trailers, the system is formulated recursively using transformation matrices $\mathbf{v}_i = M(\Delta\theta) \mathbf{v}_{i-1}$, where $\mathbf{v}_i = [v_i, \dot{\theta}_i]^T$, allowing for efficient state computation.

- **Testbed Setup**: Utilizes specialized test tracks to cover critical maneuvers, including sharp cornering and reverse backing scenarios.

### 3.2 Navigation Architecture and Middleware Integration

The system architecture follows a hierarchical design implemented on the ROS 2 (Humble) middleware. It integrates the **Autoware (Open-Source Autonomous Driving Stack)** as the functional software platform to manage core navigation modules and ensure a robust data pipeline:

- **System Flow**: The pipeline progresses from Perception (State sensing) -> Estimation (Bias correction) -> Optimization (Parameter tuning) -> to Control (Command execution).
- **Middleware Nodes**: Custom nodes such as `carla_bridge_node` for physics translation and specialized control nodes are integrated via ROS 2. The custom control layer is designed to replace standard Autoware control modules to handle the specific kinematics of the N-Trailer system.

### 3.3 Nonlinear Moving Horizon Estimation (NMHE)

NMHE is implemented as a receding horizon estimator to compensate for steering bias ($b_s$) by solving a constrained optimization problem over a **Sliding Window** $M$:
$$ \Phi = \min_{\hat{x}, \hat{b}_s} \sum_{j=t-M}^{t} (\|y_j - h(\hat{x}_j, \hat{b}_s)\|_V^2 + \|\hat{x}_{j+1} - f(\hat{x}_j, \hat{b}_s, u_j)\|_W^2) $$
The **Gauss-Newton Optimization** method is used to ensure real-time feasibility.

### 3.4 Adaptive NMPC Path Tracking

The NMPC controller is formulated as an **Optimal Control Problem (OCP)** to calculate the most efficient trajectory while respecting vehicle limits:

- **Cost Function Formulation**: Includes **Stage Cost** ($l$) and **Terminal Cost** ($E$) for guaranteed stability: $J = \min_{u} [ \sum_{k=0}^{H-1} l(x_k, u_k) + E(x_H) ]$
- **RK4 Discretization**: Employs Runge-Kutta 4th Order integration to maintain model fidelity during high-curvature maneuvers.

### 3.5 Meta-heuristic Optimization (GWO)

The Grey Wolf Optimizer (GWO) is integrated as an online tuning layer to automate the selection of $Q$ and $R$ weighting matrices, allowing the NMPC to adapt to varying operational conditions.

### 3.6 System Development and Technical Implementation

The implementation phase focuses on computational efficiency and real-time responsiveness:

- **Programming Stack**: Leverages **CasADi** or **acados** for high-performance C-code generation of the control and estimation solvers.
- **Integration Logic**: Logic is centralized within a ROS 2 Wrapper to minimize End-to-End latency and ensure synchronized communication between the NMHE and NMPC modules.

### 3.7 Experimental Procedure and Evaluation Framework

Performance validation is benchmarked across three trajectory types: **Line**, **S-Curve**, and **Figure-Eight**. The success of the methodology is measured via the following Key Performance Indicators (KPIs):

- **Tracking Accuracy**: Root Mean Square Error (RMSE) of lateral deviation.
- **Computational Efficiency**: Average processing time per control cycle.
- **Control Quality**: Smoothness of the steering command and prevention of Jackknifing conditions.

## 4. PRELIMINARY RESULTS

1. **Environment Setup**: Ubuntu 22.04 LTS, ROS 2 Humble, CARLA 0.9.15, and Autoware Universe have been successfully deployed.
2. **Kinematic Validation**: Recursive equations for a 4-trailer system were derived and validated in a Python simulation, accurately predicting off-tracking behavior.
3. **Middleware Integration**: The `tractor_odometry` ROS 2 package is developed to broadcast poses for all trailers in real-time.

## 5. RESEARCH PLAN (TIMELINE)

- **Phase 1**: Env Setup & Middleware (Completed)
- **Phase 2**: Modeling & Metaheuristic Study (Completed)
- **Phase 3**: Controller Framework Development (NMPC Design & Solver implementation)
- **Phase 4**: Adaptive System Integration (GWO Logic implementation)
- **Phase 5**: High-Fidelity Asset Construction (3D Modeling & Map generation)
- **Phase 6**: Validation, Analysis & Dissemination (Experimentation and Thesis writing)

## 6. SELECTED REFERENCES

1. **Liu et al. (2024)**, "Path tracking control of automated vehicles based on adaptive MPC in variable conditions", *IET Intelligent Transport Systems*.
2. **Lin et al. (2019)**, "Path tracking of autonomous vehicle based on adaptive model predictive control".
3. **Real-Time Longitudinal and Lateral State Estimation of Preceding Vehicle Based on Moving Horizon Estimation**, *IEEE Transactions on Intelligent Transportation Systems*.
4. **Distributed Control for Articulated Vehicles** (Internal Repository / Literature review collection for tractor-trailer dynamics).
5. **Kaljavesi, G., Kerbl, T., Betz, T., Mitkovskii, K., & Diermeyer, F. (2024)**, "CARLA-Autoware-Bridge: Facilitating Autonomous Driving Research with a Unified Framework for Simulation and Module Development", *2024 IEEE Intelligent Vehicles Symposium (IV)*.
6. **Zhou, Z., Rother, C., & Chen, J. (2023)**, "Event-Triggered Model Predictive Control for Autonomous Vehicle Path Tracking: Validation Using CARLA Simulator", *IEEE Transactions on Intelligent Vehicles*, vol. 8, no. 6, pp. 3547-3556.
