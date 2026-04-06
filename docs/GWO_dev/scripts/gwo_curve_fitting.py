import random
import math
import matplotlib.pyplot as plt
import numpy as np

# Automotive Problem: Curve Fitting for Tire Cornering Stiffness
# Model: Simplified Tire Model (Hyperbolic Tangent)
# Fy(alpha) = F_max * tanh( (C_alpha * alpha) / F_max )
# Where:
#   Fy = Lateral Force (N)
#   alpha = Slip Angle (degrees)
#   F_max = Maximum Grip Force (assumed known, e.g., 4000 N)
#   C_alpha = Cornering Stiffness (N/deg) --> THE UNKNOWN PARAMETER TO FIND

# Constants for Ground Truth
TRUE_C_ALPHA = 1200.0  # N/deg
F_MAX = 4000.0         # N
NOISE_LEVEL = 200.0    # N (Simulation Noise)

# Generate Synthetic Data
np.random.seed(42)
alpha_data = np.linspace(-10, 10, 50)  # Slip angles from -10 to 10 degrees
# Ground truth with noise
fy_data = F_MAX * np.tanh((TRUE_C_ALPHA * alpha_data) / F_MAX) + np.random.normal(0, NOISE_LEVEL, len(alpha_data))

def tire_model(alpha, c_alpha):
    return F_MAX * np.tanh((c_alpha * alpha) / F_MAX)

def objective_function(c_alpha):
    # Mean Squared Error (MSE)
    predictions = tire_model(alpha_data, c_alpha)
    mse = np.mean((fy_data - predictions) ** 2)
    return mse

# GWO Algorithm for 1D
def gwo_curve_fitting(search_agents_no, max_iter, lb, ub):
    alpha_pos = float('inf')
    alpha_score = float('inf')
    
    beta_pos = float('inf')
    beta_score = float('inf')
    
    delta_pos = float('inf')
    delta_score = float('inf')
    
    positions = [random.uniform(lb, ub) for _ in range(search_agents_no)]
    
    convergence_curve = []
    
    print(f"Initial Best MSE: {min([objective_function(x) for x in positions]):.6f}")

    # Initial evaluation to update Alpha, Beta, Delta
    for i in range(search_agents_no):
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
            
        print(f"Iter {t+1}: Best MSE = {alpha_score:.2f} (C_alpha = {alpha_pos:.2f})")
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    # Challenge: Search C_alpha in [500, 3000] N/deg
    print("Testing on Tire Curve Fitting (Cornering Stiffness)")
    lb, ub = 500, 3000
    best_c_alpha, min_mse, curve = gwo_curve_fitting(search_agents_no=10, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Estimated Cornering Stiffness: {best_c_alpha:.2f} N/deg")
    print(f"True Cornering Stiffness: {TRUE_C_ALPHA:.2f} N/deg")
    print(f"Final MSE: {min_mse:.2f}")
    
    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Regression Plot
    # Data points
    ax1.scatter(alpha_data, fy_data, color='gray', alpha=0.6, label='Experimental Data (Noisy)')
    
    # Best Fit Line
    x_smooth = np.linspace(-10, 10, 100)
    y_fit = tire_model(x_smooth, best_c_alpha)
    ax1.plot(x_smooth, y_fit, color='red', linewidth=3, label=f'Best Fit (C={best_c_alpha:.0f})')
    
    # True Line (for comparison)
    y_true = tire_model(x_smooth, TRUE_C_ALPHA)
    ax1.plot(x_smooth, y_true, color='green', linestyle='--', label=f'Ground Truth (C={TRUE_C_ALPHA:.0f})')
    
    ax1.set_title(f'Automotive: Tire Curve Fitting')
    ax1.set_xlabel('Slip Angle (deg)')
    ax1.set_ylabel('Lateral Force (N)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Convergence Curve
    ax2.plot(range(1, len(curve)+1), curve, marker='o', color='brown', linewidth=2)
    ax2.set_title('Convergence Curve: MSE Minimization')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Mean Squared Error')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/curve_fitting_combined.png')
    print("Plot saved to pict/curve_fitting_combined.png")
