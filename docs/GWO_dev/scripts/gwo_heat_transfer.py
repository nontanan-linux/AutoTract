import random
import math
import matplotlib.pyplot as plt
import numpy as np

# Forensic Science Problem: Estimating Time of Death via Heat Transfer
# Model: Newton's Law of Cooling
# T(t) = T_env + (T_body_initial - T_env) * exp(-k * t)
# Objective: Find time 't' (hours) that minimizes the error between Calculated Temp and Measured Temp.

# Constants
T_body_initial = 37.0  # Normal Body Temp (Celcius)
T_env = 25.0           # Room Temperature
k = 0.25               # Cooling Constant (approx for human body in air)
T_measured = 31.0      # Corpse Temperature found at the scene

def cooling_model(t):
    return T_env + (T_body_initial - T_env) * math.exp(-k * t)

def objective_function(t):
    # We want to find t such that cooling_model(t) approx T_measured
    estimated_temp = cooling_model(t)
    error = abs(estimated_temp - T_measured)
    return error

# GWO Algorithm for 1D
def gwo_heat_transfer(search_agents_no, max_iter, lb, ub):
    alpha_pos = float('inf')
    alpha_score = float('inf')
    
    beta_pos = float('inf')
    beta_score = float('inf')
    
    delta_pos = float('inf')
    delta_score = float('inf')
    
    positions = [random.uniform(lb, ub) for _ in range(search_agents_no)]
    
    convergence_curve = []
    
    print(f"Initial Best Error: {min([objective_function(x) for x in positions]):.6f}")

    for t in range(max_iter):
        a = 2 - t * (2 / max_iter)
        
        for i in range(search_agents_no):
            r1 = random.random(); r2 = random.random()
            A1 = 2 * a * r1 - a; C1 = 2 * r2
            D_alpha = abs(C1 * alpha_pos - positions[i])
            X1 = alpha_pos - A1 * D_alpha
            
            r1 = random.random(); r2 = random.random()
            A2 = 2 * a * r1 - a; C2 = 2 * r2
            D_beta = abs(C2 * beta_pos - positions[i])
            X2 = beta_pos - A2 * D_beta
            
            r1 = random.random(); r2 = random.random()
            A3 = 2 * a * r1 - a; C3 = 2 * r2
            D_delta = abs(C3 * delta_pos - positions[i])
            X3 = delta_pos - A3 * D_delta
            
            positions[i] = (X1 + X2 + X3) / 3
            
            # Boundary check
            if positions[i] > ub: positions[i] = ub
            if positions[i] < lb: positions[i] = lb
            
            # Update leaders
            fitness = objective_function(positions[i])
            if fitness < alpha_score:
                alpha_score = fitness
                alpha_pos = positions[i]
            elif fitness < beta_score:
                beta_score = fitness
                beta_pos = positions[i]
            elif fitness < delta_score:
                delta_score = fitness
                delta_pos = positions[i]
            
        print(f"Iter {t+1}: Best Error = {alpha_score:.6f} (at t = {alpha_pos:.4f} hrs)")
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    # Challenge: Search in [0, 10] hours since death
    print("Testing on Heat Transfer (Time of Death)")
    lb, ub = 0, 10
    best_time, min_error, curve = gwo_heat_transfer(search_agents_no=10, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Estimated Time Since Death: {best_time:.4f} hours")
    print(f"Estimated Body Temp at that time: {cooling_model(best_time):.4f} C")
    print(f"Target Measured Temp: {T_measured:.4f} C")
    
    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Physical Model Plot (Temperature vs Time)
    x = np.linspace(lb, ub, 100)
    y_temp = [cooling_model(xi) for xi in x]
    
    ax1.plot(x, y_temp, linewidth=2, label='Body Temp Cooling Curve')
    ax1.axhline(y=T_measured, color='orange', linestyle='--', label=f'Measured Temp ({T_measured}C)')
    ax1.scatter(best_time, cooling_model(best_time), color='red', s=100, zorder=5, label=f'Estimated Time ({best_time:.2f}h)')
    
    ax1.set_title(f'Forensic Model: Newton\'s Law of Cooling')
    ax1.set_xlabel('Time Since Death (Hours)')
    ax1.set_ylabel('Body Temperature (C)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Convergence Curve (Error minimization)
    ax2.plot(range(1, len(curve)+1), curve, marker='o', color='purple', linewidth=2)
    ax2.set_title('Convergence Curve: Error Minimization')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Abs Error (Temp Diff)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/heat_transfer_combined.png')
    print("Plot saved to pict/heat_transfer_combined.png")
