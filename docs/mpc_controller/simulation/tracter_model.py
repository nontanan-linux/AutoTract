import numpy as np

class TractorTrailerModel:
    """
    Kinematic model for a Tractor with N Trailers.
    State: [x, y, theta0, theta1, theta2, ..., theta_{2N}, v]
    where theta0 is tractor orientation, 
    theta_{2i-1} is drawbar orientation of trailer i,
    theta_{2i} is body orientation of trailer i.
    """
    def __init__(self, L0, trailers_config, dt=0.1):
        """
        Args:
            L0 (float): Tractor wheelbase
            trailers_config (list of dict): List containing {'L_bar': ..., 'L_trl': ..., 'dh_prev': ...}
            dt (float): Time step
        """
        self.L0 = L0
        self.trailers = trailers_config
        self.num_trailers = len(trailers_config)
        self.dt = dt
        
        # State indices
        self.IDX_X = 0
        self.IDX_Y = 1
        self.IDX_THETA0 = 2
        # Trailer angles follow at 3, 4, 5, 6...
        self.IDX_V = 3 + 2 * self.num_trailers

    def get_state_derivative(self, state, delta, a):
        """
        Calculate state derivative dx/dt.
        state: [x, y, theta0, ..., theta_{2N}, v]
        delta: steering angle
        a: acceleration
        """
        v = state[self.IDX_V]
        theta0 = state[self.IDX_THETA0]
        
        # 1. Tractor derivatives
        dx = v * np.cos(theta0)
        dy = v * np.sin(theta0)
        dtheta0 = (v / self.L0) * np.tan(delta)
        
        # 2. Recursive calculation for trailers
        # Each step returns [v_curr, dtheta_curr]
        v_prev_vec = np.array([v, dtheta0])
        theta_prev = theta0
        
        d_trailer_thetas = []
        
        for i, config in enumerate(self.trailers):
            idx_db = 3 + 2*i
            idx_tr = 3 + 2*i + 1
            
            theta_db = state[idx_db]
            theta_tr = state[idx_tr]
            
            # Drawbar (Transform A)
            v_db_vec = self._transform_A(v_prev_vec, theta_prev, theta_db, config['L_bar'], config['dh_prev'])
            d_trailer_thetas.append(v_db_vec[1]) # dtheta_db
            
            # Trailer Body (Transform B)
            v_tr_vec = self._transform_B(v_db_vec, theta_db, theta_tr, config['L_trl'])
            d_trailer_thetas.append(v_tr_vec[1]) # dtheta_tr
            
            # Update for next iteration
            v_prev_vec = v_tr_vec
            theta_prev = theta_tr
            
        # 3. Velocity derivative
        dv = a
        
        # Assemble full derivative vector
        derivatives = [dx, dy, dtheta0] + d_trailer_thetas + [dv]
        return np.array(derivatives)

    def _transform_A(self, v_prev, theta_prev, theta_curr, L_bar, d_h_prev):
        delta_theta = theta_prev - theta_curr
        c, s = np.cos(delta_theta), np.sin(delta_theta)
        M_A = np.array([
            [c, d_h_prev * s],
            [(1/L_bar) * s, -(d_h_prev/L_bar) * c]
        ])
        return M_A @ v_prev

    def _transform_B(self, v_prev, theta_prev, theta_curr, L_trl):
        delta_theta = theta_prev - theta_curr
        c, s = np.cos(delta_theta), np.sin(delta_theta)
        M_B = np.array([
            [c, 0],
            [(1/L_trl) * s, 0]
        ])
        return M_B @ v_prev

    def update(self, state, delta, a):
        """Update state using Runge-Kutta 4th order"""
        k1 = self.get_state_derivative(state, delta, a)
        k2 = self.get_state_derivative(state + self.dt/2 * k1, delta, a)
        k3 = self.get_state_derivative(state + self.dt/2 * k2, delta, a)
        k4 = self.get_state_derivative(state + self.dt * k3, delta, a)
        
        new_state = state + (self.dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)
        return new_state

    def get_unit_positions(self, state):
        """
        Calculate (x, y) coordinates for all units (Tractor rear, Trailer axles).
        Used for visualization and distance checking.
        """
        x0, y0, theta0 = state[0], state[1], state[2]
        positions = [(x0, y0)] # Tractor Rear Axle
        
        p_prev = np.array([x0, y0])
        theta_prev = theta0
        
        for i, config in enumerate(self.trailers):
            theta_db = state[3 + 2*i]
            theta_tr = state[3 + 2*i + 1]
            
            # Hitch Point
            h_curr = p_prev - config['dh_prev'] * np.array([np.cos(theta_prev), np.sin(theta_prev)])
            # Dolly Axle
            p_dolly = h_curr - config['L_bar'] * np.array([np.cos(theta_db), np.sin(theta_db)])
            # Trailer Axle
            p_trailer = p_dolly - config['L_trl'] * np.array([np.cos(theta_tr), np.sin(theta_tr)])
            
            positions.append(tuple(p_trailer))
            
            # Update for next
            p_prev = p_trailer
            theta_prev = theta_tr
            
        return positions
