#!/usr/bin/env python3
import os
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Odometry, Path
from autoware_auto_planning_msgs.msg import Trajectory
from autoware_auto_control_msgs.msg import AckermannControlCommand
import numpy as np
import math
import casadi as ca
import yaml
from ament_index_python.packages import get_package_share_directory

class NMPCController:
    """
    Nonlinear Model Predictive Controller using CasADi and IPOPT.
    Based on Kinematic Bicycle Model with Rear Axle Reference.
    """
    def __init__(self, config):
        self.N = config['mpc']['prediction_horizon']
        self.dt = config['mpc']['prediction_dt']
        self.L = config['vehicle']['wheelbase']
        
        # Weights
        self.q_ey = config['mpc']['weights']['lat_error']
        self.q_etheta = config['mpc']['weights']['heading_error']
        self.q_ev = config['mpc']['weights']['velocity_error']
        
        self.r_steer = config['mpc']['weights']['steering_input']
        self.r_accel = config['mpc']['weights']['acceleration_input']
        
        self.rd_steer = config['mpc']['weights']['steer_rate']
        self.rd_accel = config['mpc']['weights']['steer_acc'] # Using steer_acc as accel rate weight
        
        # Constraints
        self.max_steer = config['vehicle']['max_steer']
        self.max_accel = config['vehicle']['max_accel']
        self.min_accel = -config['mpc']['constraints'].get('acceleration_limit', 3.0)
        
        self.setup_optimizer()

    def setup_optimizer(self):
        self.opti = ca.Opti()
        
        # --- Decision Variables ---
        # States: [X, Y, theta, v]
        self.X = self.opti.variable(4, self.N + 1)
        # Inputs: [delta, a]
        self.U = self.opti.variable(2, self.N)
        
        # --- Parameters ---
        # Initial State
        self.x0_param = self.opti.parameter(4)
        # Reference Trajectory: [xr, yr, thetar, vr] for each step
        self.ref_param = self.opti.parameter(4, self.N + 1)
        # Previous Input (for rate constraints/costs)
        self.u_prev_param = self.opti.parameter(2)
        
        # --- Cost Function ---
        cost = 0
        for k in range(self.N):
            # Error calculation relative to reference
            xr = self.ref_param[0, k]
            yr = self.ref_param[1, k]
            thetar = self.ref_param[2, k]
            vr = self.ref_param[3, k]
            
            x = self.X[0, k]
            y = self.X[1, k]
            theta = self.X[2, k]
            v = self.X[3, k]
            
            # Lateral Error: e_y = -(X - Xr)sin(thetar) + (Y - Yr)cos(thetar)
            dx = x - xr
            dy = y - yr
            e_y = -dx * ca.sin(thetar) + dy * ca.cos(thetar)
            
            # Heading Error: e_theta = theta - thetar
            e_theta = theta - thetar
            # Normalize e_theta (using atan2(sin, cos) for symbolic compatibility)
            e_theta = ca.atan2(ca.sin(e_theta), ca.cos(e_theta))
            
            # Velocity Error: e_v = v - vr
            e_v = v - vr
            
            # Stage Cost
            cost += self.q_ey * e_y**2
            cost += self.q_etheta * e_theta**2
            cost += self.q_ev * e_v**2
            
            # Control Effort Cost
            cost += self.r_steer * self.U[0, k]**2
            cost += self.r_accel * self.U[1, k]**2
            
            # Smoothness Cost (Rate of change)
            if k == 0:
                cost += self.rd_steer * (self.U[0, k] - self.u_prev_param[0])**2
                cost += self.rd_accel * (self.U[1, k] - self.u_prev_param[1])**2
            else:
                cost += self.rd_steer * (self.U[0, k] - self.U[0, k-1])**2
                cost += self.rd_accel * (self.U[1, k] - self.U[1, k-1])**2
        
        # Terminal Cost
        dx_n = self.X[0, self.N] - self.ref_param[0, self.N]
        dy_n = self.X[1, self.N] - self.ref_param[1, self.N]
        thetar_n = self.ref_param[2, self.N]
        e_yn = -dx_n * ca.sin(thetar_n) + dy_n * ca.cos(thetar_n)
        e_thetan = ca.atan2(ca.sin(self.X[2, self.N] - thetar_n), ca.cos(self.X[2, self.N] - thetar_n))
        e_vn = self.X[3, self.N] - self.ref_param[3, self.N]
        
        cost += self.q_ey * e_yn**2 + self.q_etheta * e_thetan**2 + self.q_ev * e_vn**2
        
        self.opti.minimize(cost)
        
        # --- Constraints ---
        # Initial Condition
        self.opti.subject_to(self.X[:, 0] == self.x0_param)
        
        for k in range(self.N):
            # Kinematic Bicycle Model Dynamics (Euler)
            # x_next = x + dt * f(x, u)
            x_next = self.X[0, k] + self.dt * self.X[3, k] * ca.cos(self.X[2, k])
            y_next = self.X[1, k] + self.dt * self.X[3, k] * ca.sin(self.X[2, k])
            theta_next = self.X[2, k] + self.dt * (self.X[3, k] * ca.tan(self.U[0, k]) / self.L)
            v_next = self.X[3, k] + self.dt * self.U[1, k]
            
            self.opti.subject_to(self.X[0, k+1] == x_next)
            self.opti.subject_to(self.X[1, k+1] == y_next)
            self.opti.subject_to(self.X[2, k+1] == theta_next)
            self.opti.subject_to(self.X[3, k+1] == v_next)
            
            # Actuator Limits
            self.opti.subject_to(self.opti.bounded(-self.max_steer, self.U[0, k], self.max_steer))
            self.opti.subject_to(self.opti.bounded(self.min_accel, self.U[1, k], self.max_accel))
        
        # Solver Options
        opts = {
            'ipopt.print_level': 0,
            'print_time': 0,
            'ipopt.max_iter': 100,
            'ipopt.tol': 1e-4,
            'ipopt.warm_start_init_point': 'yes'
        }
        self.opti.solver('ipopt', opts)

    def solve(self, x0, ref_traj, u_prev):
        # Set parameters
        self.opti.set_value(self.x0_param, x0)
        self.opti.set_value(self.ref_param, ref_traj)
        self.opti.set_value(self.u_prev_param, u_prev)
        
        # Initial guess (Warm-start)
        # Shift previous solution if available, or just use current state
        try:
            sol = self.opti.solve()
            u_opt = sol.value(self.U[:, 0])
            x_pred = sol.value(self.X)
            # Set initial guess for next time
            self.opti.set_initial(self.X, sol.value(self.X))
            self.opti.set_initial(self.U, sol.value(self.U))
            return u_opt, x_pred
        except Exception as e:
            print(f"Solver failed: {e}")
            # Fallback: simple stop or previous command
            return np.array([0.0, -1.0]), None

class NMPCControllerNode(Node):
    def __init__(self):
        super().__init__('nmpc_controller_node')
        
        # Load Configuration
        try:
            share_dir = get_package_share_directory('tracter_control')
            config_path = os.path.join(share_dir, 'config/mpc_config.yaml')
        except Exception:
            # Fallback for standalone execution
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, '../config/mpc_config.yaml')
            if not os.path.exists(config_path):
                # Another fallback
                config_path = os.path.expanduser('~/AutoTract/tracter_ws/src/tracter_control/config/mpc_config.yaml')
            
        if not os.path.exists(config_path):
            self.get_logger().error(f"Config file NOT FOUND at {config_path}")
            raise FileNotFoundError(f"MPC Config not found at {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.controller = NMPCController(self.config)
        
        # ROS 2 Interfaces
        self.control_pub = self.create_publisher(AckermannControlCommand, self.config['system']['control_cmd_topic'], 10)
        self.pred_path_pub = self.create_publisher(Path, '/predicted_trajectory', 10)
        
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.traj_sub = self.create_subscription(Trajectory, self.config['path_smoothing']['ref_traj_topic'] + "_data", self.traj_callback, 10)
        
        # State variables
        self.current_state = None # [x, y, theta, v]
        self.full_ref_points = None # Full list of TrajectoryPoints
        self.ref_traj = None      # Current horizon [4, N+1]
        self.u_prev = np.array([0.0, 0.0])
        
        # Timer for control loop
        self.dt = self.config['system']['dt']
        self.timer = self.create_timer(self.dt, self.timer_callback)
        
        self.get_logger().info("NMPC Controller Node Started")

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        # Quaternion to Yaw
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        v = msg.twist.twist.linear.x
        self.current_state = np.array([x, y, yaw, v])

    def find_nearest_index(self, state, ref_points):
        # ref_points: list of TrajectoryPoint
        if not ref_points: return 0
        dists = []
        for p in ref_points:
            dx = p.pose.position.x - state[0]
            dy = p.pose.position.y - state[1]
            dists.append(dx**2 + dy**2)
        return np.argmin(dists)

    def traj_callback(self, msg):
        # Just store the full trajectory
        self.full_ref_points = msg.points
        if self.current_state is None:
            self.get_logger().info("Received trajectory, waiting for odom...")
        else:
            self.get_logger().info(f"Received trajectory with {len(msg.points)} points")

    def update_reference_horizon(self):
        if self.current_state is None or self.full_ref_points is None:
            return False
            
        # 1. Find nearest point on the full trajectory based on CURRENT state
        nearest_idx = self.find_nearest_index(self.current_state, self.full_ref_points)
        
        # 2. Extract horizon starting from nearest point
        N = self.controller.N
        ref = np.zeros((4, N + 1))
        num_pts = len(self.full_ref_points)
        
        for i in range(N + 1):
            idx = min(nearest_idx + i, num_pts - 1)
            p = self.full_ref_points[idx]
            ref[0, i] = p.pose.position.x
            ref[1, i] = p.pose.position.y
            # Yaw from quaternion
            q = p.pose.orientation
            siny_cosp = 2 * (q.w * q.z + q.x * q.y)
            cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
            ref[2, i] = math.atan2(siny_cosp, cosy_cosp)
            ref[3, i] = p.longitudinal_velocity_mps
            
        self.ref_traj = ref
        return True

    def timer_callback(self):
        # Update reference horizon every loop to ensure we track the point IN FRONT of us
        if not self.update_reference_horizon():
            return
            
        # Solve NMPC
        u_opt, x_pred = self.controller.solve(self.current_state, self.ref_traj, self.u_prev)
        
        # Publish Control Command
        cmd = AckermannControlCommand()
        cmd.stamp = self.get_clock().now().to_msg()
        cmd.lateral.steering_tire_angle = float(u_opt[0])
        cmd.longitudinal.speed = float(self.ref_traj[3, 0])
        cmd.longitudinal.acceleration = float(u_opt[1])
        self.control_pub.publish(cmd)
        
        self.u_prev = u_opt
        
        # Publish Predicted Path
        if x_pred is not None:
            self.publish_predicted_path(x_pred)

    def publish_predicted_path(self, x_pred):
        path = Path()
        path.header.frame_id = "map"
        path.header.stamp = self.get_clock().now().to_msg()
        
        for i in range(x_pred.shape[1]):
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x_pred[0, i]
            pose.pose.position.y = x_pred[1, i]
            path.poses.append(pose)
            
        self.pred_path_pub.publish(path)

def main(args=None):
    rclpy.init(args=args)
    node = NMPCControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
