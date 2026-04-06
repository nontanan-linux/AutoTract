import random
import math
import matplotlib.pyplot as plt
import numpy as np

# Engineering Problem: Optimal Maintenance Interval
# Objective: Minimize Total Cost per Unit Time
# Cost = (Maintenance Cost / Interval) + (Failure Cost * Probability of Failure / Interval)
# Let:
# Cm (Preventive Maintenance Cost) = $500
# Cf (Corrective Failure Cost) = $2500
# Beta (Weibull Shape Factor) = 2.5 (Wear-out phase)
# Eta (Weibull Scale Factor/Life) = 1000 hours
# Model: Total Cost(t) = (Cm + Cf * F(t)) / t
# Where F(t) = 1 - exp(-(t/Eta)^Beta) is the probability of failure by time t

Cm = 500
Cf = 2500
Beta = 2.5
Eta = 1000

def objective_function(t):
    # Avoid division by zero
    if t <= 1: return float('inf')
    
    # Probability of failure
    prob_failure = 1 - math.exp(- (t / Eta) ** Beta)
    
    # Total Cost per hour
    total_cost = (Cm + Cf * prob_failure) / t
    return total_cost

# GWO Algorithm for 1D
def gwo_maintenance(search_agents_no, max_iter, lb, ub):
    alpha_pos = float('inf')
    alpha_score = float('inf')
    
    beta_pos = float('inf')
    beta_score = float('inf')
    
    delta_pos = float('inf')
    delta_score = float('inf')
    
    positions = [random.uniform(lb, ub) for _ in range(search_agents_no)]
    
    convergence_curve = []
    
    # Initial evaluation
    for i in range(search_agents_no):
         # Boundary check (simple clamping)
        if positions[i] > ub: positions[i] = ub
        if positions[i] < lb: positions[i] = lb
        
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
            
    print(f"Initial Best Score: {alpha_score:.6f}")

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
            
        print(f"Iter {t+1}: Best Cost = ${alpha_score:.2f}/hr (at t = {alpha_pos:.2f} hrs)")
        convergence_curve.append(alpha_score)

    return alpha_pos, alpha_score, convergence_curve

if __name__ == "__main__":
    # Challenge: Search in [100, 2000] hours
    print("Testing on Maintenance Interval Optimization")
    lb, ub = 100, 2000
    best_time, min_cost, curve = gwo_maintenance(search_agents_no=10, max_iter=20, lb=lb, ub=ub)
    print("\n--- Optimization Result ---")
    print(f"Optimal Interval: {best_time:.2f} hours")
    print(f"Minimum Cost: ${min_cost:.2f} per hour")
    
    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Cost Curve
    x = np.linspace(lb, ub, 1000)
    y = [objective_function(xi) for xi in x]
    
    ax1.plot(x, y, linewidth=2, label='Total Cost Curve')
    ax1.scatter(best_time, min_cost, color='red', s=100, zorder=5, label=f'Optimal ({best_time:.0f}h, ${min_cost:.2f})')
    ax1.set_title(f'Engineering Trade-off: Cost vs Interval')
    ax1.set_xlabel('Maintenance Interval (Hours)')
    ax1.set_ylabel('Cost ($/hour)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Convergence Curve
    ax2.plot(range(1, len(curve)+1), curve, marker='o', color='blue', linewidth=2)
    ax2.set_title('Convergence Curve: Cost Minimization')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Cost ($/hr)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('pict/maintenance_combined.png')
    print("Plot saved to pict/maintenance_combined.png")
