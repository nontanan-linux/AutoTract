import random
import math

import matplotlib.pyplot as plt

# Objective Function: Step Function (1D)
# f(x) = (round(x + 0.5))^2  which is equivalent to floor(x+0.5)^2 usually used as Step function
# Global Minimum at x in [-0.5, 0.5] (approx), f(x)=0
def objective_function(x):
    return (math.floor(x + 0.5))**2

# GWO Algorithm for 1D
def gwo_1d_step(search_agents_no, max_iter, lb, ub):
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
    # Challenge: Search in [-10, 10]
    print("Testing on Step Function (Discontinuous)")
    lb, ub = -10, 10
    best_x, best_score, curve = gwo_1d_step(search_agents_no=10, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Optimal x found: {best_x:.6f}")
    print(f"Optimal f(x): {best_score:.6f}")
    
    # Plotting
    import numpy as np
    
    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Search Space Plot
    x = np.linspace(lb, ub, 1000)
    y = [objective_function(xi) for xi in x]
    
    ax1.plot(x, y, linewidth=2, label='Step Function')
    # Highlight the range [-0.5, 0.5] where f(x) = 0
    ax1.axvspan(-0.5, 0.5, color='red', alpha=0.3, label='Global Optimum Range')
    ax1.set_title(f'Search Space: Step Function (floor(x+0.5)^2)')
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Convergence Curve
    ax2.plot(range(1, len(curve)+1), curve, marker='o', color='orange', linewidth=2)
    ax2.set_title('Convergence Curve')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Fitness (Score)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/step_combined.png')
    print("Plot saved to pict/step_combined.png")
