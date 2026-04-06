import random
import math
import numpy as np
import matplotlib.pyplot as plt

# 6.2 3D Optimization: 3-Link Planar Robot Arm (Inverse Kinematics)
# Problem: Find joint angles (theta1, theta2, theta3) to reach target (x, y)
# Objective: Minimize distance between end-effector and target

# Robot Arm Parameters
L1 = 1.0  # Length of link 1
L2 = 1.0  # Length of link 2
L3 = 1.0  # Length of link 3
BASE_X = 0.5 # Base X position
BASE_Y = 0.5 # Base Y position

def forward_kinematics(theta):
    # theta = [t1, t2, t3]
    t1, t2, t3 = theta[0], theta[1], theta[2]
    
    # Joint 1
    x1 = BASE_X + L1 * math.cos(t1)
    y1 = BASE_Y + L1 * math.sin(t1)
    
    # Joint 2
    x2 = x1 + L2 * math.cos(t1 + t2)
    y2 = y1 + L2 * math.sin(t1 + t2)
    
    # End-Effector (Joint 3 tip)
    x3 = x2 + L3 * math.cos(t1 + t2 + t3)
    y3 = y2 + L3 * math.sin(t1 + t2 + t3)
    
    # Return all joint positions for plotting
    return np.array([[BASE_X, BASE_Y], [x1, y1], [x2, y2], [x3, y3]])

def objective_function(theta, target_pos):
    # theta terms are within [-pi, pi] usually
    positions = forward_kinematics(theta)
    tip_pos = positions[-1]
    
    # Minimize Euclidean distance to target
    error = np.linalg.norm(tip_pos - target_pos)
    return error

def gwo_ik_3d(target_pos, search_agents_no=20, max_iter=50):
    dim = 3 # 3-DOF
    lb = -math.pi # Lower bound (-180 deg)
    ub = math.pi  # Upper bound (180 deg)
    
    # Initialize positions
    positions = np.random.uniform(lb, ub, (search_agents_no, dim))
    
    alpha_pos = np.zeros(dim); alpha_score = float('inf')
    beta_pos = np.zeros(dim); beta_score = float('inf')
    delta_pos = np.zeros(dim); delta_score = float('inf')
    
    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        
        for i in range(search_agents_no):
            # Clip bounds
            positions[i] = np.clip(positions[i], lb, ub)
            
            # Calculate fitness
            fitness = objective_function(positions[i], target_pos)
            
            if fitness < alpha_score:
                alpha_score = fitness; alpha_pos = positions[i].copy()
            elif fitness < beta_score:
                beta_score = fitness; beta_pos = positions[i].copy()
            elif fitness < delta_score:
                delta_score = fitness; delta_pos = positions[i].copy()
        
        # Update positions
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
    # Generate Spiral Trajectory (Centered at BASE)
    t = np.linspace(0, 4*np.pi, 50) # 2 loops
    r = np.linspace(1.0, 2.8, 50)   # Radius increasing (min dist 1.0m, max reach < 3.0)
    x_traj = BASE_X + r * np.cos(t)
    y_traj = BASE_Y + r * np.sin(t)
    
    solved_thetas = []
    final_errors = []
    
    print("Solving Inverse Kinematics for 3-Link Arm (Spiral Path)...")
    
    # Solve IK for each point
    prev_theta = np.zeros(3) # Warm start hint? No, GWO is global, but we can restart randomly
    
    for i in range(len(t)):
        target = np.array([x_traj[i], y_traj[i]])
        
        # Run GWO
        # Increase iter for better convergent in 3D
        best_theta, err = gwo_ik_3d(target, search_agents_no=30, max_iter=30)
        
        solved_thetas.append(best_theta)
        final_errors.append(err)
        
        if i % 10 == 0:
            print(f"Point {i}: Target=({target[0]:.2f}, {target[1]:.2f}), Error={err:.4f}")
            
    avg_error = np.mean(final_errors)
    print(f"\nAverage Tracking Error: {avg_error:.4f} m")
    
    # --- Visualization ---
    try:
        plt.style.use('seaborn-whitegrid')
    except:
        plt.style.use('ggplot')
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Trajectory Tracking Setup
    ax1.set_xlim(-3.5, 4.0); ax1.set_ylim(-3.0, 4.0)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_title(f'1. 3-Link Arm Tracking (Avg Error={avg_error:.4f}m)', fontsize=14)
    ax1.set_xlabel('X Position (m)')
    ax1.set_ylabel('Y Position (m)')
    
    # Plot Reference Path
    ax1.plot(x_traj, y_traj, 'k--', linewidth=2, label='Reference Path')
    
    # Plot Traced Path (End-effector)
    tip_x = []
    tip_y = []
    
    # Plot Arm configuration every N steps
    step_plot = 5
    colors = plt.cm.viridis(np.linspace(0, 1, len(solved_thetas)))
    
    for i, theta in enumerate(solved_thetas):
        joints = forward_kinematics(theta)
        tip_x.append(joints[-1, 0])
        tip_y.append(joints[-1, 1])
        
        if i % step_plot == 0:
            # Draw Arm
            ax1.plot(joints[:, 0], joints[:, 1], 'o-', color=colors[i], alpha=0.6, linewidth=2, markersize=6)
            
    # Plot Tip Trace
    ax1.plot(tip_x, tip_y, 'r-', linewidth=1.5, alpha=0.8, label='GWO Solution')
    ax1.scatter(tip_x, tip_y, s=10, c='red', alpha=0.5)
    ax1.legend(loc='upper right')
    
    # 2. Joint Angles
    solved_thetas = np.array(solved_thetas)
    ax2.plot(solved_thetas[:, 0], label=r'$\theta_1$', linewidth=2)
    ax2.plot(solved_thetas[:, 1], label=r'$\theta_2$', linewidth=2)
    ax2.plot(solved_thetas[:, 2], label=r'$\theta_3$', linewidth=2)
    ax2.set_title('2. Joint Angles Profile', fontsize=14)
    ax2.set_xlabel('Waypoint Index')
    ax2.set_ylabel('Angle (rad)')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('pict/gwo_3d_arm_opt.png', dpi=300)
    print("Plot saved to pict/gwo_3d_arm_opt.png")
