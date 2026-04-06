import random
import math
import matplotlib.pyplot as plt
import numpy as np

# Control Systems Problem: 1D PID Tuning for Adaptive Cruise Control (ACC)
# Scenario:
# - Simulation Time: 200 seconds
# - Search Agents: 100
# - Lead Vehicle: Starts from Standstill (v=0), waits 10s, then accelerates.
# - Ego Vehicle: Must maintain safe distance of 10 meters.
# - Controller: P-Controller (Force = Kp * Distance_Error)
# - Objective: Minimize Integral Absolute Error (IAE) of Distance

# Constants
m = 1000.0   # Mass of car (kg)
b = 50.0     # Damping coefficient (drag) (N*s/m)
dt = 0.1     # Time step (s)
T_sim = 80.0 # Total simulation time (s)
SAFE_DIST = 10.0 # Meters

def get_lead_velocity(t):
    # Stop-and-Go Profile
    if t < 10.0:
        return 0.0
    else:
        # After 10s, accelerate to cruising speed
        # Smooth ramp up using tanh or similar, then oscillate
        # t_active = t - 10
        # Ramp: 0 to ~20 m/s
        
        # Simple ramp + sine
        t_run = t - 10.0
        # Smooth acceleration phase (first 20s of running)
        ramp_factor = min(1.0, t_run / 20.0) 
        
        base_v = 15.0 * ramp_factor # Max base ~54 km/h
        variation = 5.0 * ramp_factor * math.sin(0.1 * t_run)
        
        return base_v + variation

def simulate_system(Kp):
    # Initial Conditions
    x_lead = 10.0 # Lead starts at Safe Distance (10m) -> Initial Error = 0
    x_ego = 0.0
    v_ego = 0.0   # Ego starts from standstill
    
    time = np.arange(0, T_sim, dt)
    history = {'t': [], 'dist': [], 'v_lead': [], 'v_ego': [], 'error': []}
    
    iae = 0.0   # Integral Absolute Error (Tracking Accuracy)
    effort = 0.0 # Control Effort (Fuel/Comfort)

    for t in time:
        v_lead = get_lead_velocity(t)
        
        # Update Lead Position
        x_lead += v_lead * dt
        
        # Calculate Distance Error
        actual_dist = x_lead - x_ego
        error = actual_dist - SAFE_DIST 
        
        iae += abs(error) * dt
        
        # Controller
        input_force = Kp * error
        
        # Saturation
        if input_force > 5000: input_force = 5000
        if input_force < -5000: input_force = -5000
        
        # Accumulate Squared Effort (Penalty for high force/acceleration)
        effort += (input_force**2) * dt
        
        # Dynamics
        acc_ego = (input_force - b * v_ego) / m
        
        # Update Ego
        v_ego += acc_ego * dt
        if v_ego < 0: v_ego = 0
            
        x_ego += v_ego * dt
        
        history['t'].append(t)
        history['dist'].append(actual_dist)
        history['v_lead'].append(v_lead)
        history['v_ego'].append(v_ego)
        history['error'].append(error)
        
    return iae, effort, history

def objective_function(Kp):
    if Kp < 0: return float('inf')
    
    # Run Simulation
    iae, effort, _ = simulate_system(Kp)
    
    # Cost Function
    cost = iae + (effort * 1e-6) 
    return cost

def gwo_pid(search_agents_no, max_iter, lb, ub):
    alpha_pos = float('inf'); alpha_score = float('inf')
    beta_pos = float('inf'); beta_score = float('inf')
    delta_pos = float('inf'); delta_score = float('inf')
    
    positions = [random.uniform(lb, ub) for _ in range(search_agents_no)]
    convergence_curve = []
    
    # Initial Evaluation
    for i in range(search_agents_no):
        fit = objective_function(positions[i])
        if fit < alpha_score: alpha_score = fit; alpha_pos = positions[i]
        elif fit < beta_score: beta_score = fit; beta_pos = positions[i]
        elif fit < delta_score: delta_score = fit; delta_pos = positions[i]

    print(f"Initial Best Cost: {alpha_score:.6f}")

    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        for i in range(search_agents_no):
            r1=random.random(); r2=random.random(); A1=2*a*r1-a; C1=2*r2; D_alpha=abs(C1*alpha_pos-positions[i]); X1=alpha_pos-A1*D_alpha
            r1=random.random(); r2=random.random(); A2=2*a*r1-a; C2=2*r2; D_beta=abs(C2*beta_pos-positions[i]); X2=beta_pos-A2*D_beta
            r1=random.random(); r2=random.random(); A3=2*a*r1-a; C3=2*r2; D_delta=abs(C3*delta_pos-positions[i]); X3=delta_pos-A3*D_delta
            
            positions[i] = (X1 + X2 + X3) / 3
            if positions[i] > ub: positions[i] = ub
            if positions[i] < lb: positions[i] = lb
            
            fitness = objective_function(positions[i])
            if fitness < alpha_score: alpha_score = fitness; alpha_pos = positions[i]
            elif fitness < beta_score: beta_score = fitness; beta_pos = positions[i]
            elif fitness < delta_score: delta_score = fitness; delta_pos = positions[i]
            
        print(f"Iter {t+1}: Best Cost = {alpha_score:.2f} (Kp = {alpha_pos:.2f})")
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    # Challenge: Search Kp in [100, 5000] with 50 Agents (User requested 20 iter)
    print("Testing on 1D PID ACC (Comfort Mode - 20 Iter)")
    lb, ub = 100, 5000
    best_Kp, min_cost, curve = gwo_pid(search_agents_no=50, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Optimal P-Gain (Kp): {best_Kp:.2f}")
    print(f"Minimum Cost: {min_cost:.2f}")
    
    # Plotting (3 Vertical Subplots)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12), sharex=False)
    
    final_iae, final_effort, hist = simulate_system(best_Kp)
    
    # 1. Velocity Tracking
    ax1.plot(hist['t'], hist['v_lead'], 'k--', linewidth=2.0, alpha=0.7, label='Target (Lead Speed)')
    ax1.plot(hist['t'], hist['v_ego'], 'r-', linewidth=2.5, label='Response (Ego Speed)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title(f'1. Velocity Tracking (Kp={best_Kp:.0f})')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. Distance Tracking
    ax2.plot(hist['t'], hist['dist'], 'b-', linewidth=2.0, label='Actual Distance')
    ax2.axhline(y=SAFE_DIST, color='orange', linestyle='--', linewidth=2.0, label='Safe Dist (10m)')
    ax2.set_ylabel('Distance (m)')
    ax2.set_title(f'2. Distance Tracking (IAE={final_iae:.1f}, Effort={final_effort:.1e})')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # 3. Convergence Curve
    ax3.plot(range(1, len(curve)+1), curve, marker='o', color='purple', linewidth=2)
    ax3.set_title('3. Convergence Curve')
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Cost')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/pid_cruise_combined.png')
    print("Plot saved to pict/pid_cruise_combined.png")
