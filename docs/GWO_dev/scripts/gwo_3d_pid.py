import random
import math
import matplotlib.pyplot as plt
import numpy as np

# 6.1 3D Optimization: PID Controller Tuning
# Problem: Optimize Kp, Ki, Kd for ACC (Adaptive Cruise Control)
# Exact same scenario as 4.8 (Stop-and-Go) but with full PID

# Constants
m = 1000.0   # Mass (kg)
b = 50.0     # Drag (N*s/m)
dt = 0.1     # Time step (s)
T_sim = 80.0 # Time (s)
SAFE_DIST = 10.0

def get_lead_velocity(t):
    if t < 10: return 0.0
    # Stop-and-Go Profile (same as gwo_pid_cruise.py)
    t_run = t - 10.0
    ramp_factor = min(1.0, t_run / 20.0) 
    base_v = 15.0 * ramp_factor 
    variation = 5.0 * ramp_factor * math.sin(0.1 * t_run)
    return base_v + variation

def simulate_system(K):
    # K = [Kp, Ki, Kd]
    Kp, Ki, Kd = K[0], K[1], K[2]
    
    x_lead = 10.0
    x_ego = 0.0
    v_ego = 0.0
    
    integral_error = 0.0
    prev_error = 0.0
    
    iae = 0.0
    effort = 0.0
    
    history = {'t': [], 'error': [], 'v_lead': [], 'v_ego': [], 'dist': []}

    for t in np.arange(0, T_sim, dt):
        v_lead = get_lead_velocity(t)
        x_lead += v_lead * dt
        
        actual_dist = x_lead - x_ego
        error = actual_dist - SAFE_DIST
        
        # PID Logic
        integral_error += error * dt
        derivative_error = (error - prev_error) / dt
        
        # Force Constraint (Engine/Brake limit)
        input_force = (Kp * error) + (Ki * integral_error) + (Kd * derivative_error)
        input_force = max(-5000, min(5000, input_force))
        
        # Cost Calculation
        iae += abs(error) * dt
        effort += (input_force**2) * dt
        
        # Plant Dynamics (Car)
        acc_ego = (input_force - b * v_ego) / m
        v_ego += acc_ego * dt
        if v_ego < 0: v_ego = 0
        x_ego += v_ego * dt
        
        prev_error = error
        
        history['t'].append(t)
        history['error'].append(error)
        history['v_lead'].append(v_lead)
        history['v_ego'].append(v_ego)
        history['dist'].append(actual_dist)
        
    return iae, effort, history

def objective_function(K):
    # Search Space Constraints check
    if any(k < 0 for k in K): return float('inf')
    
    iae, effort, _ = simulate_system(K)
    
    # Cost Function: Minimize Error + Control Effort
    # Same as 5.2
    w_error = 1.0
    w_effort = 1e-7 
    return (w_error * iae) + (w_effort * effort)

def gwo_pid_3d(search_agents_no, max_iter, lb, ub):
    dim = 3 # 3D Problem
    positions = np.random.uniform(lb, ub, (search_agents_no, dim))
    
    alpha_pos = np.zeros(dim); alpha_score = float('inf')
    beta_pos = np.zeros(dim); beta_score = float('inf')
    delta_pos = np.zeros(dim); delta_score = float('inf')
    
    print(f"Optimizing PID (Kp, Ki, Kd)...")
    
    curve = []
    
    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        for i in range(search_agents_no):
            positions[i] = np.clip(positions[i], lb, ub)
            fitness = objective_function(positions[i])
            
            if fitness < alpha_score: alpha_score = fitness; alpha_pos = positions[i].copy()
            elif fitness < beta_score: beta_score = fitness; beta_pos = positions[i].copy()
            elif fitness < delta_score: delta_score = fitness; delta_pos = positions[i].copy()
            
        curve.append(alpha_score)
        
        # Update
        for i in range(search_agents_no):
            for j in range(dim):
                r1=random.random(); r2=random.random(); A1=2*a*r1-a; C1=2*r2
                D_alpha=abs(C1*alpha_pos[j]-positions[i, j]); X1=alpha_pos[j]-A1*D_alpha
                r1=random.random(); r2=random.random(); A2=2*a*r1-a; C2=2*r2
                D_beta=abs(C1*beta_pos[j]-positions[i, j]); X2=beta_pos[j]-A2*D_beta
                r1=random.random(); r2=random.random(); A3=2*a*r1-a; C3=2*r2
                D_delta=abs(C1*delta_pos[j]-positions[i, j]); X3=delta_pos[j]-A3*D_delta
                positions[i, j] = (X1 + X2 + X3) / 3
                
    return alpha_pos, alpha_score, curve

if __name__ == "__main__":
    # Challenge: Tune 3 parameters
    lb = [100, 0.1, 0.1]     # Lower bounds
    ub = [5000, 100, 5000]   # Upper bounds (Kd can be large)
    
    best_K, min_cost, curve = gwo_pid_3d(30, 30, lb, ub) # 30 agents, 30 iter
    
    print(f"\n--- Optimization Result (3D PID) ---")
    print(f"Kp: {best_K[0]:.2f}")
    print(f"Ki: {best_K[1]:.4f}")
    print(f"Kd: {best_K[2]:.2f}")
    print(f"Minimum Cost: {min_cost:.4f}")
    
    # Simulate Best & Comparison
    # Compare with P-Only (Kp=2000) from 4.8 (approx)
    _, _, hist_base = simulate_system([2000, 0, 0])
    _, _, hist_opt = simulate_system(best_K)
    
    # Plotting (3 Vertical Subplots with improved aesthetics)
    try:
        plt.style.use('seaborn-whitegrid')
    except:
        plt.style.use('ggplot')

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 14), sharex=False)
    
    # 1. Velocity Tracking
    ax1.plot(hist_opt['t'], hist_opt['v_lead'], color='#2c3e50', linestyle='--', linewidth=2.5, label='Lead Car (Target)')
    ax1.plot(hist_opt['t'], hist_opt['v_ego'], color='#e74c3c', linewidth=2.5, alpha=0.9, label='Ego Car (PID)')
    ax1.set_ylabel('Velocity (m/s)', fontsize=12, fontweight='bold')
    ax1.set_title(f'1. Velocity Response (3D Optimized: Kp={best_K[0]:.0f}, Ki={best_K[1]:.2f}, Kd={best_K[2]:.0f})', fontsize=14)
    ax1.legend(loc='upper left', frameon=True, shadow=True, fontsize=11)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # 2. Distance Tracking
    ax2.plot(hist_opt['t'], hist_opt['dist'], color='#2980b9', linewidth=2.5, label='Actual Distance')
    ax2.axhline(y=SAFE_DIST, color='#27ae60', linestyle='--', linewidth=2.5, label=f'Safe Distance ({SAFE_DIST}m)')
    # Add shaded region for "Good" zone (+- 0.5m)
    ax2.fill_between(hist_opt['t'], SAFE_DIST-0.5, SAFE_DIST+0.5, color='#27ae60', alpha=0.15, label='Tolerance Zone (±0.5m)')
    
    ax2.set_ylabel('Distance (m)', fontsize=12, fontweight='bold')
    ax2.set_title(f'2. Distance Keeping (Min Cost={min_cost:.4f})', fontsize=14)
    ax2.legend(loc='upper right', frameon=True, shadow=True, fontsize=11)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    # 3. Convergence Curve
    iterations = range(1, len(curve)+1)
    ax3.plot(iterations, curve, marker='o', color='#8e44ad', linewidth=2.5, markersize=8, label='Best Cost')
    ax3.set_title('3. Optimization Convergence (Cost vs Iteration)', fontsize=14)
    ax3.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Cost Function (J)', fontsize=12, fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.7)
    ax3.legend(loc='upper right', fontsize=11)
    ax3.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    plt.savefig('pict/pid_3d_opt.png', dpi=300) # Higher DPI for clarity
    print("Plot saved to pict/pid_3d_opt.png")
