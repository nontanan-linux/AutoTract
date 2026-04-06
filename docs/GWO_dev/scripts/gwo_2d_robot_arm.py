import random
import math
import matplotlib.pyplot as plt
import numpy as np

# 5.4 Robotics Inverse Kinematics: 2-Link Planar Arm Trajectory Tracking
# Problem: Find joint angles (theta1, theta2) to reach target coordinate (x,y)
# Objective: Minimize Position Error (Euclidean Distance)

# Robot Constants
L1 = 1.0  # Length of Link 1
L2 = 1.0  # Length of Link 2

def forward_kinematics(theta):
    # theta = [theta1, theta2] (radians)
    t1 = theta[0]
    t2 = theta[1]
    
    # Joint 1 (Base is 0,0)
    x1 = L1 * math.cos(t1)
    y1 = L1 * math.sin(t1)
    
    # End Effector
    x_tip = x1 + L2 * math.cos(t1 + t2)
    y_tip = y1 + L2 * math.sin(t1 + t2)
    
    return np.array([x_tip, y_tip]), np.array([x1, y1])

def objective_function(theta, target_pos):
    # theta = [theta1, theta2]
    tip_pos, _ = forward_kinematics(theta)
    
    # Cost = Distance to Target
    error_x = tip_pos[0] - target_pos[0]
    error_y = tip_pos[1] - target_pos[1]
    return math.sqrt(error_x**2 + error_y**2)

def gwo_ik(target_pos, search_agents_no=20, max_iter=15, lb=[-np.pi, -np.pi], ub=[np.pi, np.pi]):
    # GWO adapted for single-point IK
    dim = 2
    positions = np.random.uniform(lb, ub, (search_agents_no, dim))
    
    alpha_pos = np.zeros(dim); alpha_score = float('inf')
    beta_pos = np.zeros(dim); beta_score = float('inf')
    delta_pos = np.zeros(dim); delta_score = float('inf')
    
    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        for i in range(search_agents_no):
            positions[i] = np.clip(positions[i], lb, ub)
            fitness = objective_function(positions[i], target_pos)
            
            if fitness < alpha_score: alpha_score = fitness; alpha_pos = positions[i].copy()
            elif fitness < beta_score: beta_score = fitness; beta_pos = positions[i].copy()
            elif fitness < delta_score: delta_score = fitness; delta_pos = positions[i].copy()
            
        for i in range(search_agents_no):
            for j in range(dim):
                r1=random.random(); r2=random.random(); A1=2*a*r1-a; C1=2*r2
                D_alpha=abs(C1*alpha_pos[j]-positions[i, j]); X1=alpha_pos[j]-A1*D_alpha
                r1=random.random(); r2=random.random(); A2=2*a*r1-a; C2=2*r2
                D_beta=abs(C1*beta_pos[j]-positions[i, j]); X2=beta_pos[j]-A2*D_beta
                r1=random.random(); r2=random.random(); A3=2*a*r1-a; C3=2*r2
                D_delta=abs(C1*delta_pos[j]-positions[i, j]); X3=delta_pos[j]-A3*D_delta
                positions[i, j] = (X1 + X2 + X3) / 3
                
    return alpha_pos, alpha_score

if __name__ == "__main__":
    print("Simulating 2-Link Arm Trajectory Tracking...")
    
    # Generate Trajectory (Spiral)
    num_points = 60
    # Spiral: 1.5 turns (0 to 3*pi)
    t_vals = np.linspace(0, 3*math.pi, num_points)
    
    # Radius grows from 0.3 to 0.8
    # r = a + b * theta
    r_vals = np.linspace(0.3, 0.8, num_points)
    
    center_x, center_y = 1.0, 1.0
    
    target_x = center_x + r_vals * np.cos(t_vals)
    target_y = center_y + r_vals * np.sin(t_vals)
    
    actual_x = []
    actual_y = []
    joint_angles = []
    
    total_error = 0.0
    
    # Track Trajectory
    for i in range(num_points):
        target = np.array([target_x[i], target_y[i]])
        
        # Run GWO for this point
        # Use previous solution (if exists) to seed or just random start?
        # For simplicity, standard random start GWO for each point
        best_theta, min_err = gwo_ik(target, search_agents_no=20, max_iter=20)
        
        # Get result position
        tip, _ = forward_kinematics(best_theta)
        
        actual_x.append(tip[0])
        actual_y.append(tip[1])
        joint_angles.append(best_theta)
        total_error += min_err
        
        if i % 10 == 0:
            print(f"Point {i}/{num_points}: Target=({target[0]:.2f}, {target[1]:.2f}) -> Error={min_err:.4f}")

    print(f"\nAverage Tracking Error: {total_error/num_points:.4f} m")

    # Plotting
    plt.figure(figsize=(10, 6))
    
    # 1. Trajectory Trace
    plt.subplot(1, 2, 1)
    plt.plot(target_x, target_y, 'k--', label='Reference Path (Spiral)')
    plt.plot(actual_x, actual_y, 'b.-', label='Arm Trajectory (GWO)', markersize=4)
    plt.scatter([0], [0], color='black', marker='s', s=100, label='Base')
    
    # Draw a few arm configurations (e.g., every 10th point)
    for i in range(0, num_points, 10):
        theta = joint_angles[i]
        tip, elbow = forward_kinematics(theta)
        # Plot Link 1
        plt.plot([0, elbow[0]], [0, elbow[1]], 'g-', alpha=0.3, linewidth=2)
        # Plot Link 2
        plt.plot([elbow[0], tip[0]], [elbow[1], tip[1]], 'r-', alpha=0.3, linewidth=2)
        
    plt.title(f'2-Link Arm Trajectory Tracking\nAvg Error: {total_error/num_points:.4f}m')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    
    # 2. Joint Angles over Time
    plt.subplot(1, 2, 2)
    ja = np.array(joint_angles)
    plt.plot(ja[:, 0], label='Theta 1 (Base)', color='green')
    plt.plot(ja[:, 1], label='Theta 2 (Elbow)', color='red')
    plt.title('Joint Angles Profile')
    plt.xlabel('Step')
    plt.ylabel('Angle (rad)')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/robot_arm_opt.png')
    print("Plot saved to pict/robot_arm_opt.png")
