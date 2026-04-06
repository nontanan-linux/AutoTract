import random
import math

import matplotlib.pyplot as plt

# Objective Function: Quartic Function with Noise (1D)
# f(x) = x^4 + random(0, 1)
# Global Minimum at x=0, f(x) <= 1 (approx, depends on noise)
# This tests the algorithm's ability to optimize in the presence of uncertainty.
def objective_function(x):
    return x**4 + random.uniform(0, 1)

# GWO Algorithm for 1D
def gwo_1d_noisy(search_agents_no, max_iter, lb, ub):
    alpha_pos = float('inf')
    alpha_score = float('inf')
    
    beta_pos = float('inf')
    beta_score = float('inf')
    
    delta_pos = float('inf')
    delta_score = float('inf')
    
    positions = [random.uniform(lb, ub) for _ in range(search_agents_no)]
    
    convergence_curve = []
    
    print(f"Initial Best Score: {min([objective_function(x) for x in positions]):.6f}")

    for t in range(max_iter):
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
            
            if positions[i] > ub: positions[i] = ub
            if positions[i] < lb: positions[i] = lb
            
        print(f"Iter {t+1}: Best Score = {alpha_score:.6f} (at x = {alpha_pos:.6f})")
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    # Challenge: Search in [-1.28, 1.28] (Standard Quartic Noise Domain)
    print("Testing on Quartic Noise Function (Noisy)")
    lb, ub = -1.28, 1.28
    best_x, best_score, curve = gwo_1d_noisy(search_agents_no=10, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Optimal x found: {best_x:.6f}")
    print(f"Optimal f(x): {best_score:.6f}")
    
    # Plotting
    import numpy as np
    
    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Search Space Plot
    x = np.linspace(lb, ub, 400)
    # Plot base function
    y_base = [xi**4 for xi in x]
    # Plot noisy samples
    y_noise = [xi**4 + random.uniform(0, 1) for xi in x]
    
    ax1.plot(x, y_base, 'r--', linewidth=2, label='Base Function (x^4)')
    ax1.scatter(x, y_noise, s=5, alpha=0.3, color='blue', label='Noisy Samples')
    ax1.scatter(0, 0, color='red', s=100, zorder=10, label='Global Optimum (0,0)')
    
    ax1.set_title(f'Search Space: Quartic with Noise')
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Convergence Curve
    ax2.plot(range(1, len(curve)+1), curve, marker='o', color='brown', linewidth=2)
    ax2.set_title('Convergence Curve')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Fitness (Score)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/noisy_combined.png')
    print("Plot saved to pict/noisy_combined.png")
