import random
import math
import matplotlib.pyplot as plt
import numpy as np

# Control Systems: PI & PD Tuning for ACC (Section 5.2)
# Problem: Optimize Kp, Ki (for PI) and Kp, Kd (for PD)
# Scenario: Stop-and-Go (Same as 4.8)

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

def simulate_system(K, controller_type='PI'):
    # Reset State
    Kp = K[0]
    Ki = K[1] if len(K) > 1 else 0.0
    Kd = K[2] if len(K) > 2 else 0.0
    
    if controller_type == 'PI':
        Kp, Ki, Kd = K[0], K[1], 0.0
    elif controller_type == 'PD':
        Kp, Ki, Kd = K[0], 0.0, K[1]
    
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
        
        # PID Terms
        integral_error += error * dt
        derivative_error = (error - prev_error) / dt
        
        input_force = (Kp * error) + (Ki * integral_error) + (Kd * derivative_error)
        input_force = max(-5000, min(5000, input_force))
        
        iae += abs(error) * dt
        effort += (input_force**2) * dt
        
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

def objective_function(K, controller_type):
    if any(k < 0 for k in K): return float('inf')
    iae, effort, _ = simulate_system(K, controller_type)
    cost = iae + (effort * 1e-6)
    return cost

def gwo_pid_tune(search_agents_no, max_iter, controller_type, bounds):
    dim = 2
    lb, ub = bounds
    positions = np.random.uniform(lb, ub, (search_agents_no, dim))
    
    alpha_pos = np.zeros(dim); alpha_score = float('inf')
    beta_pos = np.zeros(dim); beta_score = float('inf')
    delta_pos = np.zeros(dim); delta_score = float('inf')
    
    convergence_curve = []
    
    print(f"Tuning {controller_type} Controller...")
    
    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        for i in range(search_agents_no):
            positions[i] = np.clip(positions[i], lb, ub)
            fitness = objective_function(positions[i], controller_type)
            
            if fitness < alpha_score:
                alpha_score = fitness; alpha_pos = positions[i].copy()
            elif fitness < beta_score:
                beta_score = fitness; beta_pos = positions[i].copy()
            elif fitness < delta_score:
                delta_score = fitness; delta_pos = positions[i].copy()
                
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
        
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    agents = 30
    iters = 20
    
    # Run Tuning
    best_pi_K, min_pi_cost, curve_pi = gwo_pid_tune(agents, iters, 'PI', ([100, 0.1], [5000, 50]))
    best_pd_K, min_pd_cost, curve_pd = gwo_pid_tune(agents, iters, 'PD', ([100, 100], [5000, 5000]))
    
    print(f"Optimal PI: Kp={best_pi_K[0]:.2f}, Ki={best_pi_K[1]:.2f}, Cost={min_pi_cost:.2f}")
    print(f"Optimal PD: Kp={best_pd_K[0]:.2f}, Kd={best_pd_K[1]:.2f}, Cost={min_pd_cost:.2f}")
    
    # VISUALIZATION: 3 Vertical Subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12), sharex=False)
    
    _, _, h_pi = simulate_system(best_pi_K, 'PI')
    _, _, h_pd = simulate_system(best_pd_K, 'PD')
    
    # 1. Velocity
    ax1.plot(h_pi['t'], h_pi['v_lead'], 'k--', linewidth=2, alpha=0.6, label='Target (Lead)')
    ax1.plot(h_pi['t'], h_pi['v_ego'], 'r-', linewidth=2, label='PI Controller')
    ax1.plot(h_pd['t'], h_pd['v_ego'], 'b-', linewidth=2, alpha=0.8, label='PD Controller')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('1. Velocity Tracking Comparison')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. Distance
    ax2.plot(h_pi['t'], h_pi['dist'], 'r-', label='PI Distance')
    ax2.plot(h_pd['t'], h_pd['dist'], 'b-', alpha=0.8, label='PD Distance')
    ax2.axhline(y=SAFE_DIST, color='orange', linestyle='--', label='Safe Dist (10m)')
    ax2.set_ylabel('Distance (m)')
    ax2.set_title('2. Distance Maintenance')
    ax2.legend(loc='lower right')
    ax2.grid(True, alpha=0.3)
    
    # 3. Convergence
    ax3.plot(range(1, len(curve_pi)+1), curve_pi, 'r-o', label='PI Cost')
    ax3.plot(range(1, len(curve_pd)+1), curve_pd, 'b-o', label='PD Cost')
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Cost Function')
    ax3.set_title('3. Convergence Curve')
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/pid_variants_compare.png')
    print("Plot saved to pict/pid_variants_compare.png")
