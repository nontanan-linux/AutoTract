import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from kinematic_model import TractorTrailerModel

def simulate():
    # --- Parameters ---
    SAVE_ANIMATION = True
    PLOT_DRAWBAR_TRAJECTORY = True
    
    # Dimensions (meters)
    L0 = 2.0        # Tractor Wheelbase
    W = 1.0         # Track Width
    
    # Trailer Configuration (N Trailers)
    # Define a list of dictionaries, one for each trailer unit
    trailers = [
        {'L_bar': 1.0, 'L_trl': 1.2, 'dh_prev': 0.5}, # Trailer 1 (dh_prev from Tractor)
        {'L_bar': 1.0, 'L_trl': 1.2, 'dh_prev': 0.5}, # Trailer 2 (dh_prev from Trailer 1)
        {'L_bar': 1.0, 'L_trl': 1.2, 'dh_prev': 0.5}, # Trailer 3
        {'L_bar': 1.0, 'L_trl': 1.2, 'dh_prev': 0.5}, # Trailer 4
    ]
    
    num_trailers = len(trailers)
    
    # Vehicle Box Dimensions
    tractor_width = 1.5
    tractor_len = 2.8
    tractor_overhang = 0.4 
    
    trailer_width = 1.5
    trailer_body_len = 2.0
    trailer_overhang = 0.4 
    
    wheel_diam = 0.6
    wheel_width = 0.3

    dt = 0.05
    T = 30.0
    
    # Initialize Model
    model = TractorTrailerModel(L0, trailers, dt=dt)
    
    # Initial state: [x0, y0, theta0] + [theta_drawbar_i, theta_trailer_i] * N
    # Size = 3 + 2*N
    state_size = 3 + 2 * num_trailers
    state = np.zeros(state_size)
    
    # Simulation
    steps = int(T / dt)
    trajectory = []
    drawbar_trajectories = [] # List to store list of drawbar coords per step
    states = []
    inputs = []
    velocities = [] 
    
    for i in range(steps):
        t = i * dt
        v0 = 2.0
        # Infinity-like pattern
        delta = np.radians(30) * np.sin(0.5 * t)
        
        states.append(state)
        inputs.append([v0, delta])
        
        # Get full kinematic vector
        q_kin = model.get_kinematic_vector(state, v0, delta)
        
        # Extract velocities for display
        current_vels = []
        for k in range(1, num_trailers + 1):
            idx = 1 + 4 * k
            if idx < len(q_kin):
                current_vels.append(q_kin[idx])
            else:
                current_vels.append(0.0)
        velocities.append(current_vels)
        
        # Get Coordinates for Trajectory (Tractor Rear Axle)
        coords = model.get_coordinates(state)
        trajectory.append(coords[0]) # p0
        
        # Collect Drawbar Coordinates (Dolly Positions)
        current_drawbars = []
        for k in range(num_trailers):
            idx_dolly = 3 + 3*k
            current_drawbars.append(coords[idx_dolly])
        drawbar_trajectories.append(current_drawbars)
        
        state = model.update(state, v0, delta)
        
    trajectory = np.array(trajectory)
    drawbar_trajectories = np.array(drawbar_trajectories) # Shape: (steps, num_trailers, 2)
    states = np.array(states)
    inputs = np.array(inputs)
    velocities = np.array(velocities)
    
    # --- Visualization ---
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal')
    ax.set_xlim(-10, 30)
    ax.set_ylim(-10, 40)
    ax.grid(True)
    
    ax.set_title(f"Tractor-Trailer Simulation ({num_trailers} Trailers)")
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    
    # Status Texts (Multiple objects for colors)
    status_texts = []
    
    # 1. Tractor Text
    t_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=10, color='blue',
                     verticalalignment='top', fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.6, edgecolor='none'))
    status_texts.append(t_text)
    
    # Colors for trailers
    cmap = plt.get_cmap('jet')
    trailer_colors = [cmap(float(k) / num_trailers) for k in range(num_trailers)]
    
    # 2. Trailer Texts
    for k in range(num_trailers):
        # Offset y position
        y_pos = 0.90 - (k * 0.05) # Adjust spacing as needed
        tr_text = ax.text(0.05, y_pos, '', transform=ax.transAxes, fontsize=10, color=trailer_colors[k],
                          verticalalignment='top', fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.6, edgecolor='none'))
        status_texts.append(tr_text)
    
    # Trace (Tractor)
    trace, = ax.plot([], [], 'b--', alpha=0.5, label='Tractor Path')
    
    # Drawbar Traces
    drawbar_traces = []
    if PLOT_DRAWBAR_TRAJECTORY:
        for k in range(num_trailers):
            color = trailer_colors[k]
            d_trace, = ax.plot([], [], '--', color=color, alpha=0.4, linewidth=1)
            drawbar_traces.append(d_trace)

    # Drawing Helpers
    def draw_box(ax, center, length, width, angle, color='gray', alpha=0.5):
        c, s = np.cos(angle), np.sin(angle)
        dx, dy = -length/2, -width/2
        rx = dx*c - dy*s
        ry = dx*s + dy*c
        rect = Rectangle((center[0]+rx, center[1]+ry), length, width, angle=np.degrees(angle), color=color, alpha=alpha, ec='black')
        ax.add_patch(rect)
        return rect

    def draw_wheels_at_axle(ax, center, angle, track_width, steered_angle=0, color='black'):
        wl_pos = center + (track_width/2) * np.array([-np.sin(angle), np.cos(angle)])
        wr_pos = center - (track_width/2) * np.array([-np.sin(angle), np.cos(angle)])
        
        wa = angle + steered_angle
        
        w_objs = []
        for w_pos in [wl_pos, wr_pos]:
            w = draw_box(ax, w_pos, wheel_diam, wheel_width, wa, color=color, alpha=1.0)
            w_objs.append(w)
        
        l, = ax.plot([wl_pos[0], wr_pos[0]], [wl_pos[1], wr_pos[1]], 'k-', lw=2)
        return w_objs + [l]

    patches_list = []

    def update_plot(i):
        for p in patches_list:
            p.remove()
        patches_list.clear()
        
        # Update Trace
        trace.set_data(trajectory[:i, 0], trajectory[:i, 1])
        
        # Update Drawbar Traces
        if PLOT_DRAWBAR_TRAJECTORY:
            for k, d_trace in enumerate(drawbar_traces):
                d_trace.set_data(drawbar_trajectories[:i, k, 0], drawbar_trajectories[:i, k, 1])
        
        state = states[i]
        v_curr = inputs[i, 0]
        delta_curr = inputs[i, 1]
        vels = velocities[i]
        
        # Update Status Texts
        # Tractor
        status_texts[0].set_text(f'Tractor V: {v_curr:.2f} m/s\nSteering: {np.degrees(delta_curr):.2f} deg')
        
        for k in range(num_trailers):
            # Indices for angles
            idx_drawbar = 3 + 2*k
            idx_trailer = 3 + 2*k + 1
            idx_prev = 2 + 2*k # Angle of previous unit (Tractor or Trailer k-1)
            
            theta_curr = state[idx_drawbar]
            theta_prev_val = state[idx_prev]
            
            # Relative Angle
            psi = theta_prev_val - theta_curr
            psi = (psi + np.pi) % (2 * np.pi) - np.pi
            
            status_texts[k+1].set_text(f'Trailer {k+1} V: {vels[k]:.2f} m/s\nDrawbar {k+1} Ang: {np.degrees(psi):.2f} deg')

        
        # --- Coordinates ---
        # coords = [p0, p0_f, h1, p1, p2, h2, p3, p4, ...]
        coords = model.get_coordinates(state)
        
        p0 = coords[0]
        p0_f = coords[1]
        theta0 = state[2]
        
        # --- Tractor Body ---
        p_tractor_c = (p0 + p0_f) / 2
        patches_list.append(draw_box(ax, p_tractor_c, tractor_len, tractor_width, theta0, color='orangered', alpha=0.5))
        
        # Tractor Wheels
        patches_list.extend(draw_wheels_at_axle(ax, p0, theta0, W)) # Rear
        patches_list.extend(draw_wheels_at_axle(ax, p0_f, theta0, W, steered_angle=delta_curr)) # Front
        
        # Tractor Tail Extension
        # Rear Face is p0 - overhang * forward
        p_tr_rear_face = p0 - tractor_overhang * np.array([np.cos(theta0), np.sin(theta0)])
        # Connect to first hitch (coords[2])
        h1 = coords[2]
        l_tr_tail, = ax.plot([p_tr_rear_face[0], h1[0]], [p_tr_rear_face[1], h1[1]], 'k-', lw=2)
        patches_list.append(l_tr_tail)
        
        # --- Trailers ---
        for k in range(num_trailers):
            # Indices in coords list
            # Trailer k (0-indexed):
            # h_{k+1}: 2 + 3*k
            # p_{dolly}: 3 + 3*k
            # p_{axle}: 4 + 3*k
            
            idx_h = 2 + 3*k
            idx_dolly = 3 + 3*k
            idx_axle = 4 + 3*k
            
            h_curr = coords[idx_h]
            p_dolly = coords[idx_dolly]
            p_axle = coords[idx_axle]
            
            # Angles
            theta_drawbar = state[3 + 2*k]
            theta_trailer = state[3 + 2*k + 1]
            
            # Drawbar
            l_db, = ax.plot([h_curr[0], p_dolly[0]], [h_curr[1], p_dolly[1]], 'k-', lw=3)
            patches_list.append(l_db)
            
            # Trailer Body
            p_trailer_c = (p_dolly + p_axle) / 2
            patches_list.append(draw_box(ax, p_trailer_c, trailer_body_len, trailer_width, theta_trailer, color='blue', alpha=0.5))
            
            # Wheels
            patches_list.extend(draw_wheels_at_axle(ax, p_dolly, theta_drawbar, W, color='black')) # Dolly
            patches_list.extend(draw_wheels_at_axle(ax, p_axle, theta_trailer, W, color='black')) # Rear
            
            # Hitch Point
            pt_h, = ax.plot(h_curr[0], h_curr[1], 'ko', ms=5)
            patches_list.append(pt_h)
            
            # Tail Extension (to next hitch or stub)
            p_tl_rear_face = p_axle - trailer_overhang * np.array([np.cos(theta_trailer), np.sin(theta_trailer)])
            
            if k < num_trailers - 1:
                # Connect to next hitch
                h_next = coords[2 + 3*(k+1)]
                l_tail, = ax.plot([p_tl_rear_face[0], h_next[0]], [p_tl_rear_face[1], h_next[1]], 'k-', lw=2)
                patches_list.append(l_tail)
            else:
                # Stub for last trailer (visual only)
                p_stub = p_tl_rear_face - 0.1 * np.array([np.cos(theta_trailer), np.sin(theta_trailer)])
                l_tail, = ax.plot([p_tl_rear_face[0], p_stub[0]], [p_tl_rear_face[1], p_stub[1]], 'k-', lw=2)
                patches_list.append(l_tail)

        return patches_list + [trace] + status_texts + drawbar_traces

    ani = animation.FuncAnimation(fig, update_plot, frames=len(states), interval=dt*1000, blit=True, repeat=False)
    
    print("Showing simulation... Close the window to continue.")
    plt.show()
    
    if SAVE_ANIMATION:
        print("Saving animation...")
        writer = animation.PillowWriter(fps=20)
        ani.save('simulation_full.gif', writer=writer)
        print("Simulation saved to simulation_full.gif")
    else:
        print("Animation save skipped.")

if __name__ == "__main__":
    simulate()
