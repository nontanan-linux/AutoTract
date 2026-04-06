# MPC Controller Concept - Trajectory Follower

This document outlines the design concept for an MPC (Model Predictive Control) trajectory follower node compatible with Autoware.

## 1. Overview
The MPC controller is responsible for generating control commands (steering angle, acceleration/deceleration) to track a reference trajectory while satisfying kinematic constraints and optimizing for passenger comfort and tracking accuracy.

## 2. System Architecture

```text
+-----------------+       /input/reference_trajectory       +------------------+
| Planning Module | --------------------------------------> |                  |
+-----------------+                                         |                  |
                                                            |                  |
+-----------------+    /input/current_kinematic_state       |                  |
|   Localization  | --------------------------------------> |  MPC Controller  |
+-----------------+                                         |                  |
                                                            |                  |
+-----------------+        /input/current_steering          |                  |
|Vehicle Interface| --------------------------------------> |                  |
+-----------------+                                         +--------+---------+
                                                                     |
                                                                     | /output/control_cmd
                                                                     v
                                                          +-----------------------+
                                                          | External Cmd Selector |
                                                          +-----------------------+

                                                          +-----------------------+
                                           . . . . . . . >|     Visualization     |
                                                          +-----------------------+
                                                          /output/predicted_trajectory
```

## 3. MPC Algorithm Formulation

The controller uses a **Kinematic Bicycle Model** to predict the vehicle's future states and an optimization solver to find the optimal control inputs.

### 3.1 Model Analysis

The MPC algorithm relies on a predictive model of the vehicle's motion. We analyze the **Kinematic Bicycle Model** at three different reference points and the **Dynamic Model** derived using Lagrangian mechanics.

#### 3.1.1 Kinematic Bicycle Model Analysis

The kinematic constraints assume no tire slip at low speeds. The equations of motion depend on the reference point used for the state vector.

**1) Reference at Rear Axle Center ($P_r$)**
This is the standard formulation.
State: $x = [x_r, y_r, \theta, v]^T$, Input: $u = [\delta, a]^T$

$$
\begin{bmatrix}
\dot{x}_r \\
\dot{y}_r \\
\dot{\theta} \\
\dot{v}
\end{bmatrix} =
\begin{bmatrix}
v \cos(\theta) \\
v \sin(\theta) \\
\frac{v \tan(\delta)}{L} \\
a
\end{bmatrix}
$$
(*Source: [Ding Yan's Article](https://dingyan89.medium.com/simple-understanding-of-kinematic-bicycle-model-81cac6420357)*)

**Inverse Kinematic:**
Calculate steering angle $\delta$ from desired yaw rate $\dot{\theta}$ and velocity $v$:
$$ \delta = \arctan\left(\frac{L \dot{\theta}}{v}\right) $$

**2) Reference at Front Axle Center ($P_f$)**
Using the velocity at the front wheel ($v_f$) as the state variable:
$$
\begin{bmatrix}
\dot{x}_f \\
\dot{y}_f \\
\dot{\theta} \\
\dot{v}
\end{bmatrix} =
\begin{bmatrix}
v \cos(\theta + \delta) \\
v \sin(\theta + \delta) \\
\frac{v \sin(\delta)}{L} \\
a
\end{bmatrix}
$$
(*Source: [Ding Yan's Article](https://dingyan89.medium.com/simple-understanding-of-kinematic-bicycle-model-81cac6420357)*)

**Inverse Kinematic:**
Calculate steering angle $\delta$ from desired yaw rate $\dot{\theta}$ and velocity $v$:
$$ \delta = \arcsin\left(\frac{L \dot{\theta}}{v}\right) $$

**3) Reference at Center of Gravity ($P_{cg}$)**
Using the velocity at the center of gravity ($v_{cg}$) as the state variable.
Let $l_r$ be the distance from rear axle to CG, and $l_f$ from front axle to CG. The side slip angle $\beta$ is given by:
$\beta = \arctan(\frac{l_r}{L} \tan(\delta))$

Equations of motion:
$$
\begin{bmatrix}
\dot{x}_{cg} \\
\dot{y}_{cg} \\
\dot{\theta} \\
\dot{v}
\end{bmatrix} =
\begin{bmatrix}
v \cos(\theta + \beta) \\
v \sin(\theta + \beta) \\
\frac{v \cos(\beta)}{L} \tan(\delta) \\
a
\end{bmatrix}
$$
(*Source: [Ding Yan's Article](https://dingyan89.medium.com/simple-understanding-of-kinematic-bicycle-model-81cac6420357)*)

**Inverse Kinematic:**
Calculate steering angle $\delta$ from desired yaw rate $\dot{\theta}$ and velocity $v$:
1. Calculate slip angle: $$ \beta = \arcsin\left(\frac{l_r \dot{\theta}}{v}\right) $$
2. Calculate steering angle: $$ \delta = \arctan\left(\frac{L \tan(\beta)}{l_r}\right) $$


#### 3.1.2 Dynamic Model (Lagrangian Derivation - Step-by-Step)

For higher speeds, we account for tire slip and inertia using **Lagrangian Mechanics**.

**Step 1: Define Generalized Coordinates**
Let the vehicle's pose in the inertial (global) frame be $q$.
$$ q = \begin{bmatrix} x \\ y \\ \psi \end{bmatrix} $$
where $(x, y)$ is the CG position and $\psi$ is the yaw angle.

**Step 2: Kinetic Energy ($T$)**
The kinetic energy is the sum of translational and rotational energy:
$$ T = \frac{1}{2} m (\dot{x}^2 + \dot{y}^2) + \frac{1}{2} I_z \dot{\psi}^2 $$
Potential energy $V = 0$ (assuming a flat surface).
The Lagrangian is $L = T - V = T$.

**Step 3: Generalized Forces ($Q$)**
We use the principle of **Virtual Work** to find the generalized forces associated with our coordinates $q$.
*   **Virtual Displacement ($\delta r$)**: An imaginary, infinitesimal change in the system's configuration consistent with the constraints, occurring without any passage of time.
*   **Virtual Work ($\delta W$)**: The work done by all active, non-conservative forces ($F_{ext}$) during this virtual displacement.
$$ \delta W = \sum F_{ext} \cdot \delta r $$

**Velocity Transformation (Inertial $\to$ Body)**
The velocity vector in the global (inertial) frame $[\dot{x}, \dot{y}]^T$ is related to the velocity in the vehicle's body-fixed frame $[u, v]^T$ by a rotation matrix based on the yaw angle $\psi$.
*   $u$: Longitudinal velocity (forward).
*   $v$: Lateral velocity (left).
$$
\begin{bmatrix} \dot{x} \\ \dot{y} \end{bmatrix} = R(\psi) \begin{bmatrix} u \\ v \end{bmatrix} = \begin{bmatrix} \cos\psi & -\sin\psi \\ \sin\psi & \cos\psi \end{bmatrix} \begin{bmatrix} u \\ v \end{bmatrix}
$$

**Virtual Displacements Relations**
Since virtual displacements follow the same kinematic relationships as velocities (but "frozen" in time), the relationship between global virtual displacements $(\delta x, \delta y)$ and body frame virtual displacements $(\delta x_b, \delta y_b)$ uses the same rotation matrix:
$$
\begin{bmatrix} \delta x \\ \delta y \end{bmatrix} = \begin{bmatrix} \cos\psi & -\sin\psi \\ \sin\psi & \cos\psi \end{bmatrix} \begin{bmatrix} \delta x_b \\ \delta y_b \end{bmatrix}
$$
Expanding this yields:
$$
\begin{aligned}
\delta x &= \cos\psi \delta x_b - \sin\psi \delta y_b \\
\delta y &= \sin\psi \delta x_b + \cos\psi \delta y_b
\end{aligned}
$$

**Forces acting in body frame:**
*   Front: $F_{x,f}, F_{y,f}$ (at distance $l_f$)
*   Rear: $F_{x,r}, F_{y,r}$ (at distance $l_r$)

Virtual work $\delta W$:
$$ \delta W = F_x \delta x_b + F_y \delta y_b + M_z \delta \psi $$
where:
$$
\begin{aligned}
F_x &= F_{x,r} + F_{x,f}\cos\delta - F_{y,f}\sin\delta \\
F_y &= F_{y,r} + F_{x,f}\sin\delta + F_{y,f}\cos\delta \\
M_z &= l_f(F_{x,f}\sin\delta + F_{y,f}\cos\delta) - l_r F_{y,r}
\end{aligned}
$$

The generalized forces $Q_i$ associated with $q_i$ are found by mapping these body forces back to the inertial frame:
$$
\begin{aligned}
Q_x &= F_x \cos\psi - F_y \sin\psi \\
Q_y &= F_x \sin\psi + F_y \cos\psi \\
Q_\psi &= M_z
\end{aligned}
$$

**Step 4: Lagrange Equations**
$$ \frac{d}{dt} \left( \frac{\partial L}{\partial \dot{q}_i} \right) - \frac{\partial L}{\partial q_i} = Q_i $$

**Equation for $x$:**
$$
\frac{d}{dt}(m\dot{x}) = m\ddot{x} = Q_x = F_x \cos\psi - F_y \sin\psi \quad (1)
$$
**Equation for $y$:**
$$
\frac{d}{dt}(m\dot{y}) = m\ddot{y} = Q_y = F_x \sin\psi + F_y \cos\psi \quad (2)
$$
**Equation for $\psi$:**
$$
\frac{d}{dt}(I_z\dot{\psi}) = I_z\ddot{\psi} = Q_\psi = M_z \quad (3)
$$

**Step 5: Express in Body Frame Equations**
Substitute $\ddot{x}$ and $\ddot{y}$ using body frame accelerations:
$$
\begin{aligned}
\ddot{x} &= (\dot{u} - v\dot{\psi})\cos\psi - (u\dot{\psi} + \dot{v})\sin\psi \\
\ddot{y} &= (\dot{u} - v\dot{\psi})\sin\psi + (u\dot{\psi} + \dot{v})\cos\psi
\end{aligned}
$$

Substitute into (1) and (2).
Multiply (1) by $\cos\psi$ and (2) by $\sin\psi$, then add:
$$ m(\dot{u} - v\dot{\psi}) = F_x $$
Multiply (1) by $-\sin\psi$ and (2) by $\cos\psi$, then add:
$$ m(\dot{v} + u\dot{\psi}) = F_y $$

**Final Equations of Motion (Matrix Form):**
$$
\begin{bmatrix}
m & 0 & 0 \\
0 & m & 0 \\
0 & 0 & I_z
\end{bmatrix}
\begin{bmatrix}
\dot{u} \\
\dot{v} \\
\dot{r}
\end{bmatrix}
+
\begin{bmatrix}
0 & -m r & 0 \\
m r & 0 & 0 \\
0 & 0 & 0
\end{bmatrix}
\begin{bmatrix}
u \\
v \\
r
\end{bmatrix}
=
\begin{bmatrix}
F_{x,r} + F_{x,f}\cos\delta - F_{y,f}\sin\delta \\
F_{y,f}\cos\delta + F_{y,r} + F_{x,f}\sin\delta \\
l_f(F_{y,f}\cos\delta + F_{x,f}\sin\delta) - l_r F_{y,r}
\end{bmatrix}
$$
(where $r = \dot{\psi}$)

**Tire Model (Linear):**
For small slip angles, $F_y = C_\alpha \alpha$.
$$
\begin{aligned}
\alpha_f &= \delta - \arctan\left(\frac{v + l_f r}{u}\right) \approx \delta - \frac{v + l_f r}{u} \\
\alpha_r &= -\arctan\left(\frac{v - l_r r}{u}\right) \approx - \frac{v - l_r r}{u}
\end{aligned}
$$

**Variable Definitions:**

| Symbol | Description | Unit |
| :--- | :--- | :--- |
| $m$ | Vehicle Mass | $kg$ |
| $I_z$ | Yaw Moment of Inertia | $kg \cdot m^2$ |
| $l_f$ | Distance from CG to Front Axle | $m$ |
| $l_r$ | Distance from CG to Rear Axle | $m$ |
| $x, y$ | Global Position of CG | $m$ |
| $\psi$ | Yaw Angle (Heading) | $rad$ |
| $u$ | Longitudinal Velocity (Body Frame) | $m/s$ |
| $v$ | Lateral Velocity (Body Frame) | $m/s$ |
| $r$ | Yaw Rate ($\dot{\psi}$) | $rad/s$ |
| $\delta$ | Steering Angle | $rad$ |
| $F_{x,f}, F_{x,r}$ | Longitudinal Tire Forces (Front, Rear) | $N$ |
| $F_{y,f}, F_{y,r}$ | Lateral Tire Forces (Front, Rear) | $N$ |
| $C_\alpha$ | Tire Cornering Stiffness | $N/rad$ |
| $\alpha_f, \alpha_r$ | Tire Slip Angles | $rad$ |


#### 3.1.3 State-Space Representations (Matrix Form)
For implementation in an MPC solver, we use the **Discrete Linearized State-Space Model**:

$$
\begin{aligned}
x[k+1] &= A_d x[k] + B_d u[k] + w[k] \\
y[k] &= C_d x[k]
\end{aligned}
$$

**Derivation of Matrices (Jacobian Linearization):**
Given the non-linear continuous system $\dot{x} = f(x, u)$ and output $y = h(x)$, we linearize around a reference point $(x_{ref}, u_{ref})$.

1.  **Matrix A (State Matrix)**: Represents how the state evolves.
    $$ A = \frac{\partial f}{\partial x} \bigg|_{x_{ref}, u_{ref}} = \begin{bmatrix} \frac{\partial f_1}{\partial x_1} & \dots & \frac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \frac{\partial f_n}{\partial x_1} & \dots & \frac{\partial f_n}{\partial x_n} \end{bmatrix} $$

2.  **Matrix B (Input Matrix)**: Represents how control inputs affect the state.
    $$ B = \frac{\partial f}{\partial u} \bigg|_{x_{ref}, u_{ref}} = \begin{bmatrix} \frac{\partial f_1}{\partial u_1} & \dots & \frac{\partial f_1}{\partial u_m} \\ \vdots & \ddots & \vdots \\ \frac{\partial f_n}{\partial u_1} & \dots & \frac{\partial f_n}{\partial u_m} \end{bmatrix} $$

3.  **Matrix C (Output Matrix)**: Maps states to outputs.
    $$ C = \frac{\partial h}{\partial x} \bigg|_{x_{ref}} $$
    *   For full state feedback ($y=x$), $h(x)=x \implies C = I$ (Identity Matrix).

**1) Kinematic Model (Linearized Error)**
Linearized around reference state $(x_r, y_r, \theta_r, v_r)$ and input $(\delta_r, a_r)$.

**a) Reference at Rear Axle ($P_r$)**
Applying the Jacobian to the equations:
$f_1 = v \cos\theta, \quad f_2 = v \sin\theta, \quad f_3 = \frac{v \tan\delta}{L}, \quad f_4 = a$

*   **Deriving A**:
    *   $\frac{\partial f_1}{\partial \theta} = -v \sin\theta$, $\frac{\partial f_1}{\partial v} = \cos\theta$
    *   $\frac{\partial f_2}{\partial \theta} = v \cos\theta$, $\frac{\partial f_2}{\partial v} = \sin\theta$
*   **Deriving B**:
    *   $\frac{\partial f_3}{\partial \delta} = \frac{v}{L} \sec^2\delta = \frac{v}{L \cos^2\delta}$
    *   $\frac{\partial f_4}{\partial a} = 1$

Resulting Matrices:
$$
A = \begin{bmatrix}
0 & 0 & -v_r \sin\theta_r & \cos\theta_r \\
0 & 0 & v_r \cos\theta_r & \sin\theta_r \\
0 & 0 & 0 & \frac{\tan\delta_r}{L} \\
0 & 0 & 0 & 0
\end{bmatrix}, \quad
B = \begin{bmatrix}
0 & 0 \\
0 & 0 \\
\frac{v_r}{L \cos^2\delta_r} & 0 \\
0 & 1
\end{bmatrix}
$$

**b) Reference at Front Axle ($P_f$)**
$$
A = \begin{bmatrix}
0 & 0 & -v_r \sin(\theta_r+\delta_r) & \cos(\theta_r+\delta_r) \\
0 & 0 & v_r \cos(\theta_r+\delta_r) & \sin(\theta_r+\delta_r) \\
0 & 0 & 0 & \frac{\sin\delta_r}{L} \\
0 & 0 & 0 & 0
\end{bmatrix}, \quad
B = \begin{bmatrix}
-v_r \sin(\theta_r+\delta_r) & 0 \\
v_r \cos(\theta_r+\delta_r) & 0 \\
\frac{v_r}{L} \cos\delta_r & 0 \\
0 & 1
\end{bmatrix}
$$

**c) Reference at Center of Gravity ($P_{cg}$)**
Define $\beta' = \frac{l_r/L}{\cos^2\delta_r + (l_r/L)^2 \sin^2\delta_r}$.
$$
A = \begin{bmatrix}
0 & 0 & -v_r \sin(\theta_r+\beta_r) & \cos(\theta_r+\beta_r) \\
0 & 0 & v_r \cos(\theta_r+\beta_r) & \sin(\theta_r+\beta_r) \\
0 & 0 & 0 & \frac{\cos\beta_r \tan\delta_r}{L} \\
0 & 0 & 0 & 0
\end{bmatrix}
$$
$$
B = \begin{bmatrix}
-v_r \sin(\theta_r+\beta_r) \cdot \beta' & 0 \\
v_r \cos(\theta_r+\beta_r) \cdot \beta' & 0 \\
\frac{v_r}{L} (\frac{\sec^2\delta_r}{\cos\beta_r} - \tan\delta_r \sin\beta_r \beta') & 0 \\
0 & 1
\end{bmatrix}
$$
(*Note: $P_{cg}$ linearization is complex; typically simplified by assuming small angles or $\beta \approx \frac{l_r}{L}\delta$*)

Discretization ($T_s$ sample time): $A_d = I + A T_s, B_d = B T_s$.

**2) Dynamic Model (Linearized Lateral)**
Assumptions: Constant longitudinal velocity $u$, small steering angles.
State: $x = [e_y, \dot{e}_y, e_\psi, \dot{e}_\psi]^T$ (Lateral Error, Lateral Rate, Heading Error, Yaw Rate).
Input: $u = [\delta]$.

**Continuous Form ($ \dot{x} = A x + B u $):**
$$
A = \begin{bmatrix}
0 & 1 & 0 & 0 \\
0 & -\frac{2C_f + 2C_r}{m u} & \frac{2C_f + 2C_r}{m} & \frac{-2C_f l_f + 2C_r l_r}{m u} \\
0 & 0 & 0 & 1 \\
0 & -\frac{2C_f l_f - 2C_r l_r}{I_z u} & \frac{2C_f l_f - 2C_r l_r}{I_z} & -\frac{2C_f l_f^2 + 2C_r l_r^2}{I_z u}
\end{bmatrix}, \quad
B = \begin{bmatrix}
0 \\ \frac{2C_f}{m} \\ 0 \\ \frac{2C_f l_f}{I_z}
\end{bmatrix}
$$

**Discrete Form ($ x[k+1] = A_d x[k] + B_d u[k] $):**
Using Forward Euler discretization with sampling time $T_s$:
$$
A_d = I + A T_s, \quad B_d = B T_s
$$
Substituting $A$ and $B$:
$$
A_d = \begin{bmatrix}
1 & T_s & 0 & 0 \\
0 & 1 - \frac{2C_f + 2C_r}{m u} T_s & \frac{2C_f + 2C_r}{m} T_s & \frac{-2C_f l_f + 2C_r l_r}{m u} T_s \\
0 & 0 & 1 & T_s \\
0 & -\frac{2C_f l_f - 2C_r l_r}{I_z u} T_s & \frac{2C_f l_f - 2C_r l_r}{I_z} T_s & 1 - \frac{2C_f l_f^2 + 2C_r l_r^2}{I_z u} T_s
\end{bmatrix}
$$
$$
B_d = \begin{bmatrix}
0 \\ \frac{2C_f}{m} T_s \\ 0 \\ \frac{2C_f l_f}{I_z} T_s
\end{bmatrix}
$$

#### 3.1.4 Prediction Horizon (State Rollout)
To find the optimal control inputs over a horizon $N_p$, we predict future states as a function of the current state $x[k]$, the sequence of future inputs $u$, and the disturbance sequence $w$.

**1) Single Step Prediction ($k+1$)**
$$
x[k+1] = A_d x[k] + B_d u[k] + w[k]
$$

**2) Recursive Prediction**
Substituting recursively:
$$
\begin{aligned}
x[k+1] &= A_d x[k] + B_d u[k] + w[k] \\
x[k+2] &= A_d (A_d x[k] + B_d u[k] + w[k]) + B_d u[k+1] + w[k+1] \\
       &= A_d^2 x[k] + A_d B_d u[k] + B_d u[k+1] + A_d w[k] + w[k+1] \\
x[k+3] &= A_d^3 x[k] + A_d^2 B_d u[k] + A_d B_d u[k+1] + B_d u[k+2] + A_d^2 w[k] + A_d w[k+1] + w[k+2]
\end{aligned}
$$

**3) Matrix Form (QP Formulation)**
Stacking the predicted states $X$, control inputs $U$, and disturbances $W$:
$$
X = \begin{bmatrix} x[k+1] \\ x[k+2] \\ \vdots \\ x[k+N] \end{bmatrix}, \quad
U = \begin{bmatrix} u[k] \\ u[k+1] \\ \vdots \\ u[k+N-1] \end{bmatrix}, \quad
W = \begin{bmatrix} w[k] \\ w[k+1] \\ \vdots \\ w[k+N-1] \end{bmatrix}
$$

The prediction equation becomes:
$$ X = S_x x[k] + S_u U + S_w W $$

Where:
$$
S_x = \begin{bmatrix} A_d \\ A_d^2 \\ \vdots \\ A_d^N \end{bmatrix}, \quad
S_u = \begin{bmatrix}
B_d & 0 & \dots & 0 \\
A_d B_d & B_d & \dots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
A_d^{N-1} B_d & A_d^{N-2} B_d & \dots & B_d
\end{bmatrix}, \quad
S_w = \begin{bmatrix}
I & 0 & \dots & 0 \\
A_d & I & \dots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
A_d^{N-1} & A_d^{N-2} & \dots & I
\end{bmatrix}
$$
This linear relationship allows the cost function to be written as a Quadratic Programming (QP) problem in terms of $U$.
(*Note: In standard nominal MPC, we often assume $W=0$, but it is kept here for completeness or robust formulation.*)

**4) Output Prediction**
In this case, the measurements (outputs) become:
$$ y[k] = C_d x[k] $$

The sequence of predicted outputs $Y$ over the horizon is:
$$
Y = \begin{bmatrix} y[k+1] \\ y[k+2] \\ \vdots \\ y[k+N] \end{bmatrix} =
\begin{bmatrix} C_d x[k+1] \\ C_d x[k+2] \\ \vdots \\ C_d x[k+N] \end{bmatrix}
$$
Substituting the expression for $X$:
$$ Y = \bar{C} X = \bar{C} (S_x x[k] + S_u U + S_w W) $$
Where $\bar{C} = \text{diag}(C_d, C_d, \dots, C_d)$ is a block-diagonal matrix.

### 3.2. Cost Function (Quadratic Programming Formulation)

The MPC optimization problem minimizes a cost function $J$ that balances tracking performance against control effort and smoothness.

**1) Standard Summation Form**
The cost function $J$ consists of two main parts: the **Summation Term (Stage Cost)** and the **Terminal Term (Final Cost)**.

$$
J = \underbrace{\sum_{k=0}^{N-1} L(x[k], u[k])}_{\text{Summation Term}} + \underbrace{V_f(x[N])}_{\text{Terminal Term}}
$$

Expanded form:
$$
J = \underbrace{\sum_{k=0}^{N-1} \left( ||y[k] - y_{ref}[k]||^2_Q + ||u[k]||^2_R + ||\Delta u[k]||^2_{R_d} \right)}_{\text{Summation Term (Stage Cost)}} + \underbrace{||x[N] - x_{ref}[N]||^2_P}_{\text{Terminal Term}}
$$

**A) Summation Term (Stage Cost):** Evaluated at every step $k$ from $0$ to $N-1$.
*   **Tracking Error ($ ||y - y_{ref}||^2_Q $)**:
    *   Minimizes the "cross-track error" (lateral distance from the path) and "heading error" (yaw difference).
    *   Ensures the vehicle stays on the path and points in the right direction.
*   **Control Input ($ ||u||^2_R $)**:
    *   Penalizes large control actions (e.g., large steering angles).
    *   Prevents actuator saturation and promotes energy efficiency.
*   **Control Rate ($ ||\Delta u||^2_{R_d} $)**:
    *   Penalizes rapid changes in inputs (e.g., steering rate, jerk).
    *   Crucial for **passenger comfort** and preventing oscillation (bang-bang control).

**B) Terminal Term (Final Cost):** Evaluated only at the final step $N$.
*   **Terminal Cost ($ ||x_N - x_{ref,N}||^2_P $)**:
    *   Penalizes the error at the **final command step ($N$)**.
    *   **Why indices differ**: The summation ($k=0 \dots N-1$) covers the "stage costs" while inputs are applied. The term at $N$ is the final state *after* the last input $u[N-1]$. No control input exists at $N$.
    *   Ensures stability by forcing the vehicle state to converge to the reference at the end of the horizon.

**C) Key Differences**

| Feature | Summation Term (Stage Cost) | Terminal Term (Final Cost) |
| :--- | :--- | :--- |
| **Range** | $k = 0$ to $N-1$ | $k = N$ |
| **Focus** | Trajectory following performance and smooth control actions during the movement. | Final convergence and infinite-horizon stability. |
| **Input ($u$)** | Includes input costs ($R, R_d$). | No input cost (input is not defined at $N$). |
| **Role** | Defines *how* the vehicle reaches the target (path, speed, comfort). | Defines *where* the vehicle must end up (ensures it doesn't drift away). |

**Derivation: Summation $\to$ Matrix Form (Term-by-Term)**
We transform each summation term into a matrix-vector product by "stacking" vectors over the entire horizon.

*   **1. Tracking Error Term**
    *   **Summation**: $\sum_{k=0}^{N-1} ||y[k] - y_{ref}[k]||^2_Q + ||x[N] - x_{ref}[N]||^2_P$
    *   **Understanding the Notation**: The symbol $||e||^2_Q$ is the "Weighted Squared Euclidean Norm".
        *   Just like $x^2 = x \cdot x$, for vectors we use the dot product $e^T e$.
        *   With weights: $e^T Q e$.
        *   **Why twice?**: The first $(Y-Y_{ref})^T$ is the row vector (Left side). The second $(Y-Y_{ref})$ is the column vector (Right side).
        *   Multiplying **Row $\times$ Matrix $\times$ Column** results in a **Scalar** (the single cost number).
    *   **Transformation Steps**:
        1.  Define error vector at each step: $e_k = y[k] - y_{ref}[k]$.
        2.  Stack them: $E_Y = \begin{bmatrix} e_1 \\ \vdots \\ e_N \end{bmatrix} = \begin{bmatrix} y[1] - y_{ref}[1] \\ \vdots \\ y[N] - y_{ref}[N] \end{bmatrix} = Y - Y_{ref}$.
        3.  Construct diagonal weight matrix $\mathcal{Q}$.
    *   **Matrix Form**: $(Y - Y_{ref})^T \mathcal{Q} (Y - Y_{ref})$ represents the sum of all $e_k^T Q e_k$.

*   **2. Control Input Term**
    *   **Summation**: $\sum_{k=0}^{N-1} ||u[k]||^2_R$
    *   **Understanding the Notation**:
        *   Scalar cost = $u^T R u$.
        *   **Why twice?**: Stacked input vector $U$ appears as Row ($U^T$) and Column ($U$).
        *   Multiplication: $U^T$ (Row) $\times$ $\mathcal{R}$ (Diagonal Matrix) $\times$ $U$ (Column) = **Scalar** (Total Energy Cost).
    *   **Transformation Steps**:
        1.  Define input vector at each step: $u_k = u[k]$.
        2.  Stack them: $U = \begin{bmatrix} u[0] \\ \vdots \\ u[N-1] \end{bmatrix}$.
        3.  Construct diagonal weight matrix $\mathcal{R} = \text{diag}(R, \dots, R)$.
    *   **Matrix Form**: $U^T \mathcal{R} U$

*   **3. Control Rate Term**
    *   **Summation**: $\sum_{k=0}^{N-1} ||\Delta u[k]||^2_{R_d}$
    *   **Understanding the Notation**:
        *   Scalar cost = $\Delta u^T R_d \Delta u$.
        *   **Why twice?**: Stacked rate vector $\Delta U$ appears as Row ($\Delta U^T$) and Column ($\Delta U$).
        *   Multiplication: $\Delta U^T$ (Row) $\times$ $\mathcal{R}_d$ (Diagonal Matrix) $\times$ $\Delta U$ (Column) = **Scalar** (Total Smoothness Cost).
    *   **Transformation Steps**:
        1.  Define rate vector at each step: $\Delta u_k = u[k] - u[k-1]$.
        2.  Stack them: $\Delta U = \begin{bmatrix} \Delta u[0] \\ \vdots \\ \Delta u[N-1] \end{bmatrix}$.
        3.  Construct diagonal weight matrix $\mathcal{R}_d = \text{diag}(R_d, \dots, R_d)$.
    *   **Matrix Form**: $\Delta U^T \mathcal{R}_d \Delta U$

*   **4. Example Step-by-Step (N=2) - Visualizing the "Why"**
    *   Let's look at **exactly** how the algebra works for the Input Cost term with horizon $N=2$.
    *   **Goal**: Calculate $J_{input} = u[0]^T R u[0] + u[1]^T R u[1]$ using one matrix operation.
    *   **Step A: Stacking Vectors**
We stack the individual input vectors $u[k]$ into one tall vector $U$.
$$
U = \begin{bmatrix} u[0] \\ u[1] \end{bmatrix} \quad \text{and} \quad U^T = \begin{bmatrix} u[0]^T & u[1]^T \end{bmatrix}
$$

*   **Step B: Constructing the Weight Matrix**
    *   We place the weight matrix $R$ on the diagonal of a large matrix $\mathcal{R}$. Off-diagonal blocks are zero because cost at time $k$ doesn't depend on input at time $j$.
$$
\mathcal{R} = \begin{bmatrix} R & 0 \\ 0 & R \end{bmatrix}
$$

*   **Step C: The Multiplication (The "Magic")**
    *   Calculate $U^T \mathcal{R} U$ in steps:

*   1.  **Multiply $\mathcal{R} U$ first**:
    $$
    \begin{bmatrix} R & 0 \\ 0 & R \end{bmatrix} \begin{bmatrix} u[0] \\ u[1] \end{bmatrix} = \begin{bmatrix} R u[0] + 0 \\ 0 + R u[1] \end{bmatrix} = \begin{bmatrix} R u[0] \\ R u[1] \end{bmatrix}
    $$
    *(This scales each input vector by its weight).*

*   2.  **Multiply $U^T$ by the result**:
    $$
    \begin{bmatrix} u[0]^T & u[1]^T \end{bmatrix} \begin{bmatrix} R u[0] \\ R u[1] \end{bmatrix} = \underbrace{u[0]^T (R u[0])}_{\text{Cost at k=0}} + \underbrace{u[1]^T (R u[1])}_{\text{Cost at k=1}}
    $$

*   **Result**: We recovered the summation exactly!
$$ U^T \mathcal{R} U \equiv \sum_{k=0}^{1} u[k]^T R u[k] $$
This allows us to replace the `for` loop summation with a single linear algebra operation that solvers can define as $ \frac{1}{2} x^T P x $.

**2) Matrix Form (Algebraic)**
Using the prediction vectors $Y$ and $U$ derived in the previous section:
$$
J = (Y - Y_{ref})^T \mathcal{Q} (Y - Y_{ref}) + U^T \mathcal{R} U + \Delta U^T \mathcal{R}_d \Delta U
$$
Where:
*   $\mathcal{Q}, \mathcal{R}, \mathcal{R}_d$: Block-diagonal weighting matrices.
*   **$\Delta U$ (Control Rate Vector)**: Represents the **change** in control inputs between steps.
    $$ \Delta U = \begin{bmatrix} u[0] - u[-1] \\ u[1] - u[0] \\ \vdots \\ u[N-1] - u[N-2] \end{bmatrix} $$
    *   $u[-1]$ is the previous control input applied to the system.
    *   Minimizing this term ensures **smoothness** and reduces jerk.

**3) Standard QP Form**
The Autoware MPC algorithm formulation (and standard LQR) minimizes deviations from both reference states and **reference inputs** ($U_{ref}$).
$$
J(U) = (Y - Y_{ref})^T \mathcal{Q} (Y - Y_{ref}) + (U - U_{ref})^T \mathcal{R} (U - U_{ref}) + (U - U_{ref})^T \mathcal{R}_d (U - U_{ref})
$$
*   **$U_{ref}$**: The steady-state input (e.g., steering angle required to maintain curvature).

Substituting $Y = \bar{C}(S_x x[k] + S_u U + S_w W)$, we derive the QP matrices:
$$
J(U) = \frac{1}{2} U^T H U + f^T U + \text{const}
$$

**Derivation: Matrix Form $\to$ Standard QP Form**
1.  **Define Constant Error Terms ($E_{lat}$)**:
    We separate the prediction equation $Y = \bar{C}(S_x x[k] + S_u U + S_w W)$ into two parts:
    *   **Effect of Optimization Variable ($U$)**: $\bar{C} S_u U$.
    *   **Known/Constant Terms**: Everything else (Initial state response + Disturbance).
    
    We define the "uncontrollable" error vector $E_{lat}$ as the difference between the known terms and the reference:
    $$ E_{lat} = \underbrace{\bar{C} S_x x[k]}_{\text{Free Response}} + \underbrace{\bar{C} S_w W}_{\text{Disturbance}} - Y_{ref} $$
    
    Now, the total tracking error is simply: $(Y - Y_{ref}) = \bar{C} S_u U + E_{lat}$.

2.  **Expand the Cost Function**:
    Substitute into $J(U) = ||Y - Y_{ref}||^2_\mathcal{Q} + ||U - U_{ref}||^2_\mathcal{R}$:
    $$ J = (\bar{C} S_u U + E_{lat})^T \mathcal{Q} (\bar{C} S_u U + E_{lat}) + (U - U_{ref})^T \mathcal{R} (U - U_{ref}) $$

3.  **Expand Quadratic Terms**:
    *   **Tracking Term**:
        $$ U^T (S_u^T \bar{C}^T \mathcal{Q} \bar{C} S_u) U + 2 E_{lat}^T \mathcal{Q} \bar{C} S_u U + \text{const} $$
    *   **Input Term**:
        $$ U^T \mathcal{R} U - 2 U_{ref}^T \mathcal{R} U + \text{const} $$

4.  **Group by Powers of $U$ to find $H$ and $f$**:
    MATCH with $\frac{1}{2} U^T H U + f^T U$:
    *   **Quadratic ($U^T \dots U$)**:
        $$ \frac{1}{2} H = (S_u^T \bar{C}^T \mathcal{Q} \bar{C} S_u + \mathcal{R}) \implies H = 2(S_u^T \bar{C}^T \mathcal{Q} \bar{C} S_u + \mathcal{R}) $$
    *   **Linear ($\dots U$)**:
        $$ f^T = 2 E_{lat}^T \mathcal{Q} \bar{C} S_u - 2 U_{ref}^T \mathcal{R} $$
        Taking the transpose gives $f$:
        $$ f = 2 S_u^T \bar{C}^T \mathcal{Q} E_{lat} - 2 \mathcal{R} U_{ref} $$

**Key Matrices:**
*   **H (Hessian Matrix)**: Describes the curvature of the cost function. It is positive definite (convex).
    $$ H = 2 (S_u^T \bar{C}^T \mathcal{Q} \bar{C} S_u + \mathcal{R}) $$
*   **f (Gradient Vector)**: Linear term describing the slope.
    $$ f = 2 S_u^T \bar{C}^T \mathcal{Q} (\underbrace{\bar{C} S_x x[k] + \bar{C} S_w W - Y_{ref}}_{E_{lat}}) - 2 \mathcal{R} U_{ref} $$
*(Note: If $\mathcal{R}_d$ is included for smoothing, it adds terms to $H$ and $f$ related to $\Delta U$ logic).*

#### 3.2.1 Weighting Matrix Analysis
These matrices determine the controller's behavior. They are typically **diagonal matrices** to allow tuning individual states/inputs independently.

| Matrix | Name | Characteristics | Effect of Increasing Values ($\uparrow$) |
| :--- | :--- | :--- | :--- |
| **Q** | State Weight | **Positive Semi-Definite** ($Q \succeq 0$)<br>Diagonal matrix $[q_{lat}, q_{heading}, q_{vel}]$ | **Tighter Tracking**: reduces errors ($y - y_{ref}$).<br>**Side Effect**: May cause aggressive control, overshoot, or instability if too high relative to $R/R_d$. |
| **R** | Input Weight | **Positive Definite** ($R \succ 0$)<br>Diagonal matrix $[r_{steer}, r_{accel}]$ | **Energy Efficiency**: Minimizes control magnitude.<br>**Side Effect**: Slower response, vehicle may cut corners or fail to reach target speed. |
| **Rd** | Rate Weight | **Positive Semi-Definite** ($R_d \succeq 0$)<br>Diagonal matrix $[r_{\dot{\delta}}, r_{jerk}]$ | **Smoothness**: Reduces jerk and rapid steering changes.<br>**Side Effect**: System becomes "sluggish" or delayed. Essential for passenger comfort. |
| **P** | Terminal Weight | **Positive Semi-Definite** ($P \succeq 0$)<br>Penalty on final state $x[N]$ | **Stability**: Ensures the horizon ends near the target.<br>**Side Effect**: If calculated via Algebraic Riccati Equation (ARE), guarantees infinite-horizon stability. |

**Tuning Guidelines:**
1.  Start with $R_d$ to ensure smooth, physically realizable actuation.
2.  Increase $Q$ until tracking is acceptable.
3.  If oscillatory, increase $R$ or $R_d$.
4.  $P$ is often set equal to $Q$ or solved via the Discrete Algebraic Riccati Equation (DARE) for nominal stability.

### 3.3. Apply to vehicle path-following (Kinematic Bicycle Model Reference at Rear Axle Center)
The kinematic bicycle model is inherently nonlinear, which prevents the direct application of standard linear MPC formulations. While Nonlinear MPC (NMPC) is an option, it is often computationally expensive for real-time applications. To address this, we employ **linearization** techniques. By approximating the nonlinear dynamics around the reference trajectory at each time step, we transform the system into a **Linear Time-Varying (LTV)** model. This allows the complex path tracking problem to be solved efficiently using Quadratic Programming (QP).

For a nonlinear kinematic vehicle model, the discrete-time update equations are as follows:

$$
\begin{aligned}
x_{k+1} &= x_k + v_k \cos(\theta_k) \Delta t \\
y_{k+1} &= y_k + v_k \sin(\theta_k) \Delta t \\
\theta_{k+1} &= \theta_k + \frac{v_k \tan(\delta_k)}{L} \Delta t
\end{aligned}
$$

The vehicle reference is the center of the rear axle. The states, parameters, and control variables are described below:

| Variable | Description | Unit |
| :--- | :--- | :--- |
| $x_k, y_k$ | Global coordinates of Rear Axle Center | [m] |
| $\theta_k$ | Heading angle (Yaw) | [rad] |
| $v_k$ | Vehicle linear velocity | [m/s] |
| $\delta_k$ | Steering angle | [rad] |
| $L$ | Wheelbase | [m] |
| $\Delta t$ | Sampling time | [s] |







#### 1. Error Dynamics (Rear Axle)
To control the vehicle to follow a specific path, it is more effective to formulate the system in terms of **deviation** from that path rather than using global coordinates. We transform the system into the **Frenet Frame** (path coordinates):

*   **Lateral Error ($y_k$ or $e_y$)**: Displaced distance from the path center.
*   **Heading Error ($\theta_k$ or $e_\theta$)**: Difference between vehicle yaw and path tangent.

By assuming the vehicle is close to the path, we can derive the update equations for these error states. The term $-\kappa_r$ appears in the heading update because the reference frame itself is rotating (curving) as the vehicle moves along it.

Given the nonlinear dynamics and omitting the longitudinal coordinate $x$, the resulting set of equations become:
$$
\begin{aligned}
y_{k+1} &= y_k + v \sin(\theta_k) dt \\
\theta_{k+1} &= \theta_k + \frac{v \tan(\delta_k)}{L} dt - \kappa_r v \cos(\theta_k) dt \\
\delta_{k+1} &= \delta_k - \tau^{-1} (\delta_k - \delta_{des}) dt
\end{aligned}
$$
Where $\kappa_r(s)$ is the curvature along the trajectory parametrized by the arc length.

#### 2. Linearization (Small Angle Assumption)
We linearize around the reference state ($e_y=0, e_\theta=0$) and reference input ($\delta_{ref}$).
*   **Small Angle**: $\sin(e_\theta) \approx e_\theta$.
*   **Reference Steering (Ackermann Formula)**: At lower speeds, the reference steering angle $\delta_{ref}$ required to follow a path with curvature $\kappa_r$ is approximated by the **Ackermann steering expression** (or purely geometric steering):
    $$ \delta_{ref}[k] \approx \arctan(L \kappa_r) $$
    This serves as the operating point for linearization.
*   **Input Linearization**: The term $\tan(\delta)$ is nonlinear. We approximate it using a first-order **Taylor expansion** around the reference steering angle $\delta_{ref}$ (operating point):

    General Taylor formula: $f(x) \approx f(a) + f'(a)(x - a)$
    
    Applying to $f(\delta) = \tan(\delta)$ with $a = \delta_{ref}$:
    1.  **Function Value**: $f(\delta_{ref}) = \tan(\delta_{ref})$
    2.  **Derivative**: $f'(\delta) = \frac{d}{d\delta}\tan(\delta) = \sec^2(\delta) = \frac{1}{\cos^2(\delta)}$
    3.  **Substitution**:
        $$ \tan(\delta) \approx \tan(\delta_{ref}) + \frac{1}{\cos^2(\delta_{ref})} (\delta - \delta_{ref}) $$
        Distributing the term:
        $$ \tan(\delta) \approx \underbrace{\tan(\delta_{ref}) - \frac{\delta_{ref}}{\cos^2(\delta_{ref})}}_{\text{Constant } C_k} + \underbrace{\frac{1}{\cos^2(\delta_{ref})}}_{\text{Linear Coeff. } K_k} \delta $$

#### 3. Linear Time-Varying (LTV) Model
Substituting the approximations gives the linear error dynamics:
$$
\begin{aligned}
e_y[k+1] &= e_y[k] + v e_\theta[k] \Delta t \\
e_\theta[k+1] &= e_\theta[k] + \frac{v \Delta t}{L \cos^2(\delta_{ref})} (\delta_k - \delta_{ref}[k])
\end{aligned}
$$

This results in the discrete LTV state-space form $x_{err}[k+1] = A_k x_{err}[k] + B_k \Delta \delta_k$:
$$
\begin{bmatrix} e_y \\ e_\theta \end{bmatrix}_{k+1} =
\begin{bmatrix} 1 & v \Delta t \\ 0 & 1 \end{bmatrix}
\begin{bmatrix} e_y \\ e_\theta \end{bmatrix}_k +
\begin{bmatrix} 0 \\ \frac{v \Delta t}{L \cos^2(\delta_{ref})} \end{bmatrix}
(\delta_k - \delta_{ref})
$$

### 3.4. Constraints
The problem is solved subject to the following physical and safety limits:
*   **State Constraints**: Velocity limits, position boundaries (if applicable).
*   **Input Constraints**:
    *   $\delta_{min} \leq \delta \leq \delta_{max}$ (Steering limits)
    *   $a_{min} \leq a \leq a_{max}$ (Acceleration limits)
*   **Input Rate Constraints**:
    *   $\dot{\delta}_{min} \leq \dot{\delta} \leq \dot{\delta}_{max}$ (Steering rate limits)
    *   $\dot{a}_{min} \leq \dot{a} \leq \dot{a}_{max}$ (Jerk limits)

## 4. Input Topics

The controller subscribes to the following topics to receive the planned path and current vehicle state.

| Name | topic Type | Description |
| :--- | :--- | :--- |
| `~/input/reference_trajectory` | `autoware_planning_msgs/Trajectory` | The target trajectory generated by the planning module (local planner). |
| `~/input/current_kinematic_state` | `nav_msgs/Odometry` | Current vehicle pose (position, orientation) and velocity (twist) in the map frame. |
| `~/input/current_steering` | `autoware_vehicle_msgs/SteeringReport` | Real-time feedback of the current steering angle from the vehicle interface. |

## 5. Output Topics

The generated control commands are published to be consumed by the external command selector or vehicle interface.

| Name | Topic Type | Description |
| :--- | :--- | :--- |
| `~/output/control_cmd` | `autoware_control_msgs/Control` | The computed lateral (steering) and longitudinal (velocity/accel) commands. |
| `~/output/predicted_trajectory` | `autoware_planning_msgs/Trajectory` | (Optional) The predicted vehicle path over the prediction horizon for visualization/debug. |

> **Note**: The `control_cmd` is typically routed to the `external_cmd_selector` (as the "local" or "autonomous" command source) or directly to the `vehicle_cmd_gate`, depending on the system architecture.

## 6. Services / Actions

Interfaces for state management and mode switching.

| Service Name | Service Type | Description |
| :--- | :--- | :--- |
| `~/service/reset_mpc` | `std_srvs/Trigger` | Resets the internal MPC solver state (e.g., cold start). |
| `~/service/set_parameters` | `rcl_interfaces/SetParameters` | Dynamic reconfiguration of MPC weights and constraints. |

## 7. Parameters

Configuration parameters for the vehicle model and MPC solver.

### Vehicle Parameters
*   `wheel_base`: Distance between front and rear axles (m).
*   `max_steer_angle`: Maximum steering angle limit (rad).
*   `min_steer_angle`: Minimum steering angle limit (rad).
*   `accel_limit`: Maximum acceleration limit (m/s^2).

### MPC Solver Parameters
*   `prediction_horizon`: Number of steps to predict into the future (N).
*   `dt`: Time step for the discrete model (s).
*   `weight_lat_error`: Cost weight for lateral deviation (Q_lat).
*   `weight_heading_error`: Cost weight for heading deviation (Q_theta).
*   `weight_velocity_error`: Cost weight for velocity deviation (Q_vel).
*   `weight_steer_input`: Cost weight for steering actuation (R_steer).
*   `weight_accel_input`: Cost weight for acceleration actuation (R_accel).

## 6. References
1.  **Autoware Universe Documentation**: [MPC Lateral Controller - MPC Algorithm](https://autowarefoundation.github.io/autoware.universe_planning/pr-5583/control/mpc_lateral_controller/model_predictive_control_algorithm/)
