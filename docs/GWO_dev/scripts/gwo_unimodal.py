import random
import math

# Objective Function: f(x) = x^2
def objective_function(x):
    return x**2

import matplotlib.pyplot as plt

# GWO Algorithm for 1D
def gwo_1d(search_agents_no, max_iter, lb, ub, dim=1):
    # 1. Initialize Alpha, Beta, Delta positions (scalar for 1D)
    alpha_pos = float('inf')
    alpha_score = float('inf')
    
    beta_pos = float('inf')
    beta_score = float('inf')
    
    delta_pos = float('inf')
    delta_score = float('inf')
    
    # Initialize positions of wolves
    positions = [random.uniform(lb, ub) for _ in range(search_agents_no)]
    
    convergence_curve = []
    
    print(f"Initial Best Score: {min([objective_function(x) for x in positions]):.6f}")

    # Main Loop
    for t in range(max_iter):
        
        # Calculate fitness and update Alpha, Beta, Delta
        for i in range(search_agents_no):
            fitness = objective_function(positions[i])
            
            # Update Alpha
            if fitness < alpha_score:
                alpha_score = fitness
                alpha_pos = positions[i]
            # Update Beta
            elif fitness < beta_score:
                beta_score = fitness
                beta_pos = positions[i]
            # Update Delta
            elif fitness < delta_score:
                delta_score = fitness
                delta_pos = positions[i]
        
        # a decreases linearly from 2 to 0
        a = 2 - t * (2 / max_iter)
        
        # Update position of each wolf
        for i in range(search_agents_no):
            # For 1D, vectors represent scalar operations
            r1 = random.random()
            r2 = random.random()
            
            # Alpha
            A1 = 2 * a * r1 - a
            C1 = 2 * r2
            D_alpha = abs(C1 * alpha_pos - positions[i])
            X1 = alpha_pos - A1 * D_alpha
            
            # Beta
            r1 = random.random()
            r2 = random.random()
            A2 = 2 * a * r1 - a
            C2 = 2 * r2
            D_beta = abs(C2 * beta_pos - positions[i])
            X2 = beta_pos - A2 * D_beta
            
            # Delta
            r1 = random.random()
            r2 = random.random()
            A3 = 2 * a * r1 - a
            C3 = 2 * r2
            D_delta = abs(C3 * delta_pos - positions[i])
            X3 = delta_pos - A3 * D_delta
            
            # Average
            positions[i] = (X1 + X2 + X3) / 3
            
            # Boundary check
            if positions[i] > ub: positions[i] = ub
            if positions[i] < lb: positions[i] = lb
            
        print(f"Iter {t+1}: Best Score = {alpha_score:.10f} (at x = {alpha_pos:.6f})")
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

# Configuration
if __name__ == "__main__":
    lb, ub = -10, 10
    best_x, best_score, curve = gwo_1d(search_agents_no=10, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Optimal x found: {best_x:.10f}")
    print(f"Optimal f(x): {best_score:.10f}")
    
    # Plotting
    import numpy as np
    
    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Search Space Plot
    x = np.linspace(lb, ub, 400)
    y = [objective_function(xi) for xi in x]
    
    ax1.plot(x, y, linewidth=2, label='Objective Function')
    ax1.scatter(0, objective_function(0), color='red', s=100, zorder=5, label='Global Optimum (0,0)')
    ax1.set_title(f'Search Space: Unimodal (x^2)')
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Convergence Curve
    ax2.plot(range(1, len(curve)+1), curve, marker='o', color='green', linewidth=2)
    ax2.set_title('Convergence Curve')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Fitness (Score)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/unimodal_combined.png')
    print("Plot saved to pict/unimodal_combined.png")
