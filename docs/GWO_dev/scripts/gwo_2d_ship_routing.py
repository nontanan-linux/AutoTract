import random
import math
import matplotlib.pyplot as plt
import numpy as np

# 2D Ship Routing with GWO
# Problem: Optimize ship route from Port A to Port B avoiding Storms
# Coordinates: Longitude (x), Latitude (y)

# Constants
START = np.array([10.0, 10.0])   # Start: Lon 10, Lat 10
GOAL = np.array([90.0, 60.0])    # Goal: Lon 90, Lat 60
NUM_WAYPOINTS = 6                # Number of adjustable waypoints
DIM = NUM_WAYPOINTS * 2 
LB = 0.0
UB = 100.0

# Storm Zones (Longitude, Latitude, Radius)
STORMS = [
    (40.0, 35.0, 12.0), # Major Typhoon
    (70.0, 45.0, 8.0),  # Tropical Depression
    (25.0, 15.0, 6.0)   # Local Storm
]

def check_storm_penalty(p1, p2):
    """Calculate penalty if path cuts through storms"""
    penalty = 0.0
    num_samples = 20 # Check points along the segment
    SAFETY_BUFFER = 5.0 # Keep this distance from the storm edge
    
    for i in range(num_samples + 1):
        t = i / num_samples
        point = p1 + t * (p2 - p1) # Interpolated point
        
        for (sx, sy, r) in STORMS:
            dist = np.linalg.norm(point - np.array([sx, sy]))
            
            # Penalize if within (Radius + Buffer)
            limit = r + SAFETY_BUFFER 
            if dist < limit:
                # Penalty increases if deep inside
                severity = (limit - dist) / limit
                penalty += 10000.0 * severity # Increased weight
                
    return penalty

def objective_function(position):
    waypoints = position.reshape((NUM_WAYPOINTS, 2))
    # Path: Start -> Waypoints -> Goal
    path = np.vstack([START, waypoints, GOAL])
    
    total_dist = 0.0
    total_penalty = 0.0
    
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i+1]
        
        # Distance Cost (Fuel)
        dist = np.linalg.norm(p2 - p1)
        total_dist += dist
        
        # Safety Cost (Storms)
        total_penalty += check_storm_penalty(p1, p2)
            
    return total_dist + total_penalty

def gwo_ship_routing(search_agents_no, max_iter, dim, lb, ub):
    # Initialization
    positions = np.zeros((search_agents_no, dim))
    
    # Initialize near the straight line (Heuristic Initialization)
    for i in range(search_agents_no):
        for j in range(NUM_WAYPOINTS):
            ratio = (j + 1) / (NUM_WAYPOINTS + 1)
            ideal_point = START + ratio * (GOAL - START)
            # Add randomness to explore around the straight line
            positions[i, 2*j] = ideal_point[0] + random.uniform(-10, 10)     # Lon
            positions[i, 2*j+1] = ideal_point[1] + random.uniform(-10, 10)   # Lat
            
    positions = np.clip(positions, lb, ub)
    
    alpha_pos = np.zeros(dim); alpha_score = float('inf')
    beta_pos = np.zeros(dim); beta_score = float('inf')
    delta_pos = np.zeros(dim); delta_score = float('inf')
    
    print(f"Optimizing Ship Route ({max_iter} iterations)...")
    
    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        
        for i in range(search_agents_no):
            positions[i] = np.clip(positions[i], lb, ub)
            fitness = objective_function(positions[i])
            
            if fitness < alpha_score:
                alpha_score = fitness; alpha_pos = positions[i].copy()
            elif fitness < beta_score:
                beta_score = fitness; beta_pos = positions[i].copy()
            elif fitness < delta_score:
                delta_score = fitness; delta_pos = positions[i].copy()
                
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
                
        if (t+1) % 10 == 0:
            print(f"Iter {t+1}: Cost = {alpha_score:.2f}")
            
    return alpha_pos, alpha_score

if __name__ == "__main__":
    current_best_pos, min_cost = gwo_ship_routing(search_agents_no=50, max_iter=50, dim=DIM, lb=LB, ub=UB)
    
    print("\n--- Route Optimization Complete ---")
    print(f"Minimum Cost: {min_cost:.2f}")
    
    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Storms
    for (sx, sy, r) in STORMS:
        storm = plt.Circle((sx, sy), r, color='gray', alpha=0.4, label='Storm Zone')
        ax.add_patch(storm)
        ax.text(sx, sy, 'Storm', ha='center', va='center', color='white', fontweight='bold')
        
    # Plot Start/Goal
    ax.plot(START[0], START[1], 'bo', markersize=10, label='Start Port')
    ax.text(START[0], START[1]-3, 'Port A', ha='center', color='blue')
    
    ax.plot(GOAL[0], GOAL[1], 'go', markersize=10, label='Dest Port')
    ax.text(GOAL[0], GOAL[1]+3, 'Port B', ha='center', color='green')
    
    # Plot Optimized Path
    waypoints = current_best_pos.reshape((NUM_WAYPOINTS, 2))
    path = np.vstack([START, waypoints, GOAL])
    ax.plot(path[:, 0], path[:, 1], 'r.-', linewidth=2, markersize=8, label='Optimal Route')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 80)
    ax.set_xlabel('Longitude (deg)')
    ax.set_ylabel('Latitude (deg)')
    ax.set_title(f'GWO Ship Routing (Storm Avoidance)\nTotal Cost: {min_cost:.2f}')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Remove duplicate labels in legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='lower right')
    
    plt.savefig('pict/gwo_ship_routing.png')
    print("Map saved to pict/gwo_ship_routing.png")
