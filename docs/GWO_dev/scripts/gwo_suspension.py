import random
import math
import matplotlib.pyplot as plt
import numpy as np

# 5.3 Vibration Isolation: Active/Passive Suspension Optimization (3-DOF)
# Problem: Optimize Main Suspension (ks, cs) for Passenger Comfort
# Model: 3 Degrees of Freedom (Wheel, Body, Passenger)

# System Constants
mu = 40.0     # Unsprung mass (Wheel) - kg
ms = 300.0    # Sprung mass (Car Body) - kg (1/4 car)
mp = 70.0     # Passenger Mass - kg

kt = 200000.0 # Tire stiffness (N/m)

# Standard Seat Parameters (Fixed)
kp = 15000.0  # Seat stiffness (N/m)
cp = 1000.0   # Seat damping (N*s/m)

# Simulation
dt = 0.005 # Time step (s)
T_sim = 5.0 # Simulation duration (s)

def get_road_profile(t):
    # Single bump at t=1s
    if 1.0 <= t <= 1.5:
        return 0.1 * math.sin(2 * math.pi * (t - 1.0)) # 10cm bump
    return 0.0

def simulate_system(x_opt):
    ks = x_opt[0] # Suspension stiffness
    cs = x_opt[1] # Suspension damping
    
    # State: [zu, zs, zp, vzu, vzs, vzp]
    # u=wheel, s=sprung(body), p=passenger
    state = np.zeros(6)
    
    t_span = np.arange(0, T_sim, dt)
    
    acc_p_history = [] # Passenger Accel
    zp_history = []    # Passenger Pos
    zs_history = []    # Body Pos
    zu_history = []    # Wheel Pos
    zr_history = []    # Road Input
    
    total_acc_sq = 0.0
    
    for t in t_span:
        zu, zs, zp, vzu, vzs, vzp = state
        zr = get_road_profile(t)
        
        # Forces
        # F_tire = kt * (zr - zu)  (UP on wheel)
        # F_susp = ks * (zu - zs) + cs * (vzu - vzs) (UP on body, DOWN on wheel)
        # F_seat = kp * (zs - zp) + cp * (vzs - vzp) (UP on pass, DOWN on body)
        
        f_tire = kt * (zr - zu)
        f_susp = ks * (zu - zs) + cs * (vzu - vzs)
        f_seat = kp * (zs - zp) + cp * (vzs - vzp)
        
        # Dynamics (Newton's 2nd Law)
        # mu * azu = f_tire - f_susp
        azu = (f_tire - f_susp) / mu
        
        # ms * azs = f_susp - f_seat
        azs = (f_susp - f_seat) / ms
        
        # mp * azp = f_seat
        azp = f_seat / mp
        
        # Integrate (Euler)
        state[3] += azu * dt # vzu
        state[4] += azs * dt # vzs
        state[5] += azp * dt # vzp
        
        state[0] += state[3] * dt # zu
        state[1] += state[4] * dt # zs
        state[2] += state[5] * dt # zp
        
        # Objective: Passenger Comfort (Minimize azp)
        total_acc_sq += (azp**2) * dt
        
        acc_p_history.append(azp)
        zp_history.append(zp)
        zs_history.append(zs)
        zr_history.append(zr)
        zu_history.append(zu)
        
    return total_acc_sq, t_span, zp_history, zs_history, zr_history, acc_p_history, zs_history, zu_history

def objective_function(x):
    # x = [ks, cs]
    # Constraints
    if x[0] < 1000 or x[0] > 100000: return float('inf') # ks bounds
    if x[1] < 100 or x[1] > 20000: return float('inf')   # cs bounds
    
    cost, _, _, _, _, _, _, _ = simulate_system(x)
    return cost

def gwo_suspension(search_agents_no, max_iter, lb, ub):
    dim = 2
    positions = np.random.uniform(lb, ub, (search_agents_no, dim))
    
    alpha_pos = np.zeros(dim); alpha_score = float('inf')
    beta_pos = np.zeros(dim); beta_score = float('inf')
    delta_pos = np.zeros(dim); delta_score = float('inf')
    
    print(f"Optimizing 3-DOF Suspension (Passenger Comfort)...")
    
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
            
        # Update (Standard GWO)
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
    # Baseline (Stiff/Sport)
    k_base = 80000.0
    c_base = 6000.0
    cost_base, t_base, zp_base, zs_base, zr_base, acc_base, _, _ = simulate_system([k_base, c_base])
    print(f"Baseline (k={k_base}, c={c_base}): Cost={cost_base:.4f}")

    # Optimize
    lb = [5000, 500]   # Lower bounds [k, c]
    ub = [100000, 15000] # Upper bounds [k, c]
    
    best_x, min_cost, curve = gwo_suspension(30, 30, lb, ub)
    print(f"Optimal (k={best_x[0]:.2f}, c={best_x[1]:.2f}): Cost={min_cost:.4f}")
    
    # Simulate Best
    _, t_opt, zp_opt, zs_opt, zr_opt, acc_opt, zs_opt_hist, zu_opt_hist = simulate_system(best_x)
    
    # Visualization (3 Vertical Subplots)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 14), sharex=False)
    
    # 1. Displacement Layers (Vibration Isolation)
    ax1.plot(t_base, zr_opt, 'k--', label='Road Input (Bump)', linewidth=2.0, alpha=0.6)
    ax1.plot(t_opt, zu_opt_hist, 'g:', label='Unsprung (Wheel)', linewidth=1.5, alpha=0.7)
    ax1.plot(t_opt, zs_opt_hist, 'y-.', label='Sprung (Body)', linewidth=2.0, alpha=0.8)
    ax1.plot(t_opt, zp_opt, 'b-', label='Passenger (Optimized)', linewidth=2.5)
    
    ax1.set_ylabel('Displacement (m)')
    ax1.set_title(f'1. Vibration Isolation Layers (Optimized)\nPassenger Mass={mp}kg')
    ax1.legend(loc='upper right', fontsize='small')
    ax1.grid(True, alpha=0.3)
    
    # 2. Acceleration
    ax2.plot(t_base, acc_base, 'r:', linewidth=1.5, label='Baseline')
    ax2.plot(t_opt, acc_opt, 'b-', linewidth=2, label='Optimized')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Accel (m/s^2)')
    ax2.set_title(f'2. Passenger Acceleration (Comfort Metric)\nCost: {cost_base:.2f} -> {min_cost:.2f}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Convergence Curve
    ax3.plot(range(1, len(curve)+1), curve, marker='o', color='purple', linewidth=2)
    ax3.set_title('3. Convergence Curve')
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Cost (Comfort Index)')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/suspension_opt.png')
    print("Plot saved to pict/suspension_opt.png")
