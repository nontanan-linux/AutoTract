import random
import math
import matplotlib.pyplot as plt
import numpy as np

# 2D Robot Path Planning with GWO
# Problem: Find the shortest collision-free path from Start to Goal
# Environment: 2D Grid [0, 10] x [0, 10] with circular obstacles
# Wolf Representation: A set of N intermediate waypoints (x1, y1, x2, y2, ...)
# Dimensionality: 2 * num_waypoints

# Constants
START = np.array([0.0, 0.0])
GOAL = np.array([10.0, 10.0])
NUM_WAYPOINTS = 5  # Number of intermediate points
DIM = NUM_WAYPOINTS * 2 # x and y for each waypoint
UB = 10.0
LB = 0.0

# Obstacles (x, y, radius)
OBSTACLES = [
    (3.0, 3.0, 1.5),
    (7.0, 6.0, 1.2),
    (4.0, 8.0, 1.0),
    (8.0, 2.0, 1.5)
]

def check_collision_segment(p1, p2):
    """Check if the line segment p1-p2 intersects any obstacle"""
    for (ox, oy, r) in OBSTACLES:
        # Vector from p1 to p2
        d = p2 - p1
        f = p1 - np.array([ox, oy])
        
        a = np.dot(d, d)
        b_coeff = 2*np.dot(f, d)
        c = np.dot(f, f) - r**2
        
        discriminant = b_coeff*b_coeff - 4*a*c
        if discriminant >= 0:
            discriminant = math.sqrt(discriminant)
            t1 = (-b_coeff - discriminant)/(2*a + 1e-9)
            t2 = (-b_coeff + discriminant)/(2*a + 1e-9)
            
            if (0 <= t1 <= 1) or (0 <= t2 <= 1):
                return True # Collision detected
    return False

def objective_function(position):
    # Reshape wolf position into waypoints
    waypoints = position.reshape((NUM_WAYPOINTS, 2))
    
    # Construct full path: Start -> Waypoints -> Goal
    path = np.vstack([START, waypoints, GOAL])
    
    total_length = 0.0
    penalty = 0.0
    
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i+1]
        dist = np.linalg.norm(p2 - p1)
        total_length += dist
        
        # Collision Penalty
        if check_collision_segment(p1, p2):
            penalty += 1000.0 # Heavy penalty for hitting obstacle
            
    return total_length + penalty

def gwo_path(search_agents_no, max_iter, dim, lb, ub):
    # Initialize Alpha, Beta, Delta
    alpha_pos = np.zeros(dim)
    alpha_score = float('inf')
    beta_pos = np.zeros(dim)
    beta_score = float('inf')
    delta_pos = np.zeros(dim)
    delta_score = float('inf')
    
    # Initialize positions (Simple random optimization)
    # Better initialization: Linear interpolation between Start/Goal + noise
    positions = np.zeros((search_agents_no, dim))
    for i in range(search_agents_no):
         # Create a straight line path and add random noise
         for j in range(NUM_WAYPOINTS):
             ratio = (j + 1) / (NUM_WAYPOINTS + 1)
             ideal_point = START + ratio * (GOAL - START)
             positions[i, 2*j] = ideal_point[0] + random.uniform(-2, 2)     # x
             positions[i, 2*j+1] = ideal_point[1] + random.uniform(-2, 2)   # y
    
    # Clip to bounds
    positions = np.clip(positions, lb, ub)
    
    convergence_curve = []
    
    print(f"Starting GWO for Path Planning ({max_iter} iterations)...")
    
    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        
        for i in range(search_agents_no):
            # Check Boundary
            positions[i] = np.clip(positions[i], lb, ub)
            
            # Calculate Fitness
            fitness = objective_function(positions[i])
            
            # Update Alpha, Beta, Delta
            if fitness < alpha_score:
                alpha_score = fitness
                alpha_pos = positions[i].copy()
            elif fitness < beta_score:
                beta_score = fitness
                beta_pos = positions[i].copy()
            elif fitness < delta_score:
                delta_score = fitness
                delta_pos = positions[i].copy()
        
        # Update Positions
        for i in range(search_agents_no):
            for j in range(dim):
                r1=random.random(); r2=random.random(); A1=2*a*r1-a; C1=2*r2
                D_alpha=abs(C1*alpha_pos[j]-positions[i, j]); X1=alpha_pos[j]-A1*D_alpha
                
                r1=random.random(); r2=random.random(); A2=2*a*r1-a; C2=2*r2
                D_beta=abs(C1*beta_pos[j]-positions[i, j]); X2=beta_pos[j]-A2*D_beta
                
                r1=random.random(); r2=random.random(); A3=2*a*r1-a; C3=2*r2
                D_delta=abs(C1*delta_pos[j]-positions[i, j]); X3=delta_pos[j]-A3*D_delta
                
                positions[i, j] = (X1 + X2 + X3) / 3

        print(f"Iter {t+1}: Best Path Length = {alpha_score:.4f}")
        convergence_curve.append(alpha_score)
        
    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    search_agents_no = 50
    max_iter = 100
    
    alpha_pos, best_score, curve = gwo_path(search_agents_no, max_iter, DIM, LB, UB)
    
    print("\n--- Final Results ---")
    print(f"Best Path Length: {best_score:.4f}")
    
    # Plotting
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Draw Obstacles
    for (ox, oy, r) in OBSTACLES:
        circle = plt.Circle((ox, oy), r, color='gray', alpha=0.5)
        ax.add_patch(circle)
        # Check collision zone
        ax.plot(ox, oy, 'kx')
        
    # Reconstruct Best Path
    best_waypoints = alpha_pos.reshape((NUM_WAYPOINTS, 2))
    full_path = np.vstack([START, best_waypoints, GOAL])
    
    # Plot Path
    ax.plot(full_path[:, 0], full_path[:, 1], 'r.-', linewidth=2, markersize=10, label='Optimized Path')
    ax.plot(START[0], START[1], 'bs', markersize=12, label='Start')
    ax.plot(GOAL[0], GOAL[1], 'gd', markersize=12, label='Goal')
    
    # Dummy plot for obstacle legend
    ax.plot([], [], 'o', color='gray', alpha=0.5, label='Obstacle')
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title(f'GWO Robot Path Planning (2D)\nLength: {best_score:.2f}')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    plt.savefig('pict/gwo_robot_path.png')
    print("Plot saved to pict/gwo_robot_path.png")
