import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import argparse

def create_diagram(L0=2.0, L1=1.0, L2=1.2, L3=1.0, L4=1.2, L5=1.0, L6=1.2, L7=1.0, L8=1.2, W=1.5, 
                   tractor_width=1.5, tractor_len=2.8, 
                   trailer_width=1.5, trailer_len=2.0, 
                   tail_ext=0.15, 
                   theta0_deg=45.0, theta1_deg=25.0, theta2_deg=10.0, 
                   theta3_deg=-10.0, theta4_deg=-25.0, theta5_deg=-45.0, 
                   theta6_deg=-25.0, theta7_deg=-10.0, theta8_deg=25.0,
                   save_path='kinematic_diagram_full.png'):
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    # --- Calculations ---
    # Tractor Geometry
    tractor_overhang = (tractor_len - L0) / 2
    dh = tractor_overhang + tail_ext 
    
    # Trailer 1 Geometry
    trailer_overhang = (trailer_len - L2) / 2
    dh2 = trailer_overhang + tail_ext # Hitch 2 offset
    
    # Trailer 2 Geometry
    trailer2_len = trailer_len
    trailer2_width = trailer_width
    trailer2_overhang = (trailer2_len - L4) / 2
    
    # Trailer 3 Geometry
    trailer3_len = trailer_len
    trailer3_width = trailer_width
    trailer3_overhang = (trailer3_len - L6) / 2
    dh3 = trailer3_overhang + tail_ext
    
    # Trailer 4 Geometry
    trailer4_len = trailer_len
    trailer4_width = trailer_width
    trailer4_overhang = (trailer4_len - L8) / 2

    # Wheel Dimensions
    r_wheel = 10 * 0.0254
    wheel_diam = 2 * r_wheel
    wheel_width = 0.3

    # Visualization Angles
    theta0 = np.radians(theta0_deg)
    theta1 = np.radians(theta1_deg)
    theta2 = np.radians(theta2_deg)
    theta3 = np.radians(theta3_deg)
    theta4 = np.radians(theta4_deg)
    theta5 = np.radians(theta5_deg)
    theta6 = np.radians(theta6_deg)
    theta7 = np.radians(theta7_deg)
    theta8 = np.radians(theta8_deg)
    
    delta = np.radians(25) 
    
    # Starting Position
    x0, y0 = 0, 0  # Tractor Rear Axle Center (Baselink 0)

    # --- Kinematic Points ---
    
    # Tractor
    # Front Axle:
    x0_f = x0 + L0 * np.cos(theta0)
    y0_f = y0 + L0 * np.sin(theta0)
    # Hitch 1:
    xh1 = x0 - dh * np.cos(theta0)
    yh1 = y0 - dh * np.sin(theta0)
    
    # Trailer 1
    # Dolly 1 (Front Axle of Trailer 1)
    x1 = xh1 - L1 * np.cos(theta1)
    y1 = yh1 - L1 * np.sin(theta1)
    # Trailer 1 Rear Axle
    x2 = x1 - L2 * np.cos(theta2)
    y2 = y1 - L2 * np.sin(theta2)
    # Hitch 2
    xh2 = x2 - dh2 * np.cos(theta2)
    yh2 = y2 - dh2 * np.sin(theta2)
    
    # Trailer 2
    # Dolly 2 (Front Axle of Trailer 2)
    x3 = xh2 - L3 * np.cos(theta3)
    y3 = yh2 - L3 * np.sin(theta3)
    # Trailer 2 Rear Axle
    x4 = x3 - L4 * np.cos(theta4)
    y4 = y3 - L4 * np.sin(theta4)
    # Hitch 3
    dist_hitch3 = trailer2_overhang + tail_ext
    xh3 = x4 - dist_hitch3 * np.cos(theta4)
    yh3 = y4 - dist_hitch3 * np.sin(theta4)
    
    # Trailer 3
    # Dolly 3
    x5 = xh3 - L5 * np.cos(theta5)
    y5 = yh3 - L5 * np.sin(theta5)
    # Trailer 3 Rear Axle
    x6 = x5 - L6 * np.cos(theta6)
    y6 = y5 - L6 * np.sin(theta6)
    # Hitch 4
    dist_hitch4 = trailer3_overhang + tail_ext
    xh4 = x6 - dist_hitch4 * np.cos(theta6)
    yh4 = y6 - dist_hitch4 * np.sin(theta6)
    
    # Trailer 4
    # Dolly 4
    x7 = xh4 - L7 * np.cos(theta7)
    y7 = yh4 - L7 * np.sin(theta7)
    # Trailer 4 Rear Axle
    x8 = x7 - L8 * np.cos(theta8)
    y8 = y7 - L8 * np.sin(theta8)
    
    # Trailer 4 Tail
    dist_tail_hitch4 = trailer4_overhang + tail_ext
    x_tail4 = x8 - dist_tail_hitch4 * np.cos(theta8)
    y_tail4 = y8 - dist_tail_hitch4 * np.sin(theta8)

    # --- Drawing Helpers ---
    
    def draw_wheel_pair(ax, center, angle, width, steered_angle=0, color='black'):
        cx, cy = center
        px = -np.sin(angle)
        py = np.cos(angle)
        
        wl_x = cx + (width/2) * px
        wl_y = cy + (width/2) * py
        wr_x = cx - (width/2) * px
        wr_y = cy - (width/2) * py
        
        ax.plot([wl_x, wr_x], [wl_y, wr_y], 'k-', lw=2)
        
        wa = angle + steered_angle
        
        for wx, wy in [(wl_x, wl_y), (wr_x, wr_y)]:
            c, s = np.cos(wa), np.sin(wa)
            dx, dy = -wheel_diam/2, -wheel_width/2
            rx = dx*c - dy*s
            ry = dx*s + dy*c
            rect = patches.Rectangle((wx+rx, wy+ry), wheel_diam, wheel_width, angle=np.degrees(wa), color=color)
            ax.add_patch(rect)

    def draw_chassis(ax, center, length, width, angle, color='gray', label=None):
        cx, cy = center
        c, s = np.cos(angle), np.sin(angle)
        dx, dy = -length/2, -width/2
        rx = dx*c - dy*s
        ry = dx*s + dy*c
        rect = patches.Rectangle((cx+rx, cy+ry), length, width, angle=np.degrees(angle), 
                                 linewidth=2, edgecolor='black', facecolor=color, alpha=0.3, label=label)
        ax.add_patch(rect)

    def draw_dashed_ref(ax, center, length=1.0, angle=0, color='k', style='--'):
        cx, cy = center
        dx = length * np.cos(angle)
        dy = length * np.sin(angle)
        ax.plot([cx, cx + dx], [cy, cy + dy], color=color, linestyle=style, lw=1, alpha=0.6)

    # --- Draw Vehicles ---

    # 1. Tractor
    p_tr_front_face = np.array([x0_f, y0_f]) + tractor_overhang * np.array([np.cos(theta0), np.sin(theta0)])
    p_tr_rear_face = np.array([x0, y0]) - tractor_overhang * np.array([np.cos(theta0), np.sin(theta0)])
    p_tr_c = (p_tr_front_face + p_tr_rear_face) / 2
    draw_chassis(ax, p_tr_c, tractor_len, tractor_width, theta0, color='orangered', label='Tractor')
    
    draw_wheel_pair(ax, (x0_f, y0_f), theta0, W, steered_angle=delta, color='black')
    draw_wheel_pair(ax, (x0, y0), theta0, W, color='black')
    
    ax.plot([p_tr_rear_face[0], xh1], [p_tr_rear_face[1], yh1], 'k-', lw=2)
    
    # 2. Drawbar 1
    ax.plot([xh1, x1], [yh1, y1], 'k-', lw=4)
    
    # 3. Trailer 1
    p_tl1_rear_face = np.array([x2, y2]) - trailer_overhang * np.array([np.cos(theta2), np.sin(theta2)])
    p_tl1_front_face = np.array([x1, y1]) + trailer_overhang * np.array([np.cos(theta2), np.sin(theta2)]) # Approx
    # Better center calculation:
    p_tl1_c = (np.array([x1, y1]) + np.array([x2, y2])) / 2
    draw_chassis(ax, p_tl1_c, trailer_len, trailer_width, theta2, color='blue', label='Trailer 1')
    
    draw_wheel_pair(ax, (x1, y1), theta1, W, color='black')
    draw_wheel_pair(ax, (x2, y2), theta2, W, color='black')
    
    ax.plot([p_tl1_rear_face[0], xh2], [p_tl1_rear_face[1], yh2], 'k-', lw=2)
    
    # 4. Drawbar 2
    ax.plot([xh2, x3], [yh2, y3], 'k-', lw=4)
    
    # 5. Trailer 2
    p_tl2_c = (np.array([x3, y3]) + np.array([x4, y4])) / 2
    draw_chassis(ax, p_tl2_c, trailer2_len, trailer2_width, theta4, color='blue', label='Trailer 2')
    
    draw_wheel_pair(ax, (x3, y3), theta3, W, color='black')
    draw_wheel_pair(ax, (x4, y4), theta4, W, color='black')
    
    ax.plot([x4, xh3], [y4, yh3], 'k-', lw=2)
    
    # 6. Drawbar 3
    ax.plot([xh3, x5], [yh3, y5], 'k-', lw=4)
    
    # 7. Trailer 3
    p_tl3_c = (np.array([x5, y5]) + np.array([x6, y6])) / 2
    draw_chassis(ax, p_tl3_c, trailer3_len, trailer3_width, theta6, color='blue', label='Trailer 3')
    
    draw_wheel_pair(ax, (x5, y5), theta5, W, color='black')
    draw_wheel_pair(ax, (x6, y6), theta6, W, color='black')
    
    ax.plot([x6, xh4], [y6, yh4], 'k-', lw=2)
    
    # 8. Drawbar 4
    ax.plot([xh4, x7], [yh4, y7], 'k-', lw=4)
    
    # 9. Trailer 4
    p_tl4_c = (np.array([x7, y7]) + np.array([x8, y8])) / 2
    draw_chassis(ax, p_tl4_c, trailer4_len, trailer4_width, theta8, color='blue', label='Trailer 4')
    
    draw_wheel_pair(ax, (x7, y7), theta7, W, color='black')
    draw_wheel_pair(ax, (x8, y8), theta8, W, color='black')
    
    ax.plot([x8, x_tail4], [y8, y_tail4], 'k-', lw=2)

    # Hitch Points
    ax.plot(xh1, yh1, 'ko', ms=6)
    ax.plot(xh2, yh2, 'ko', ms=6)
    ax.plot(xh3, yh3, 'ko', ms=6)
    ax.plot(xh4, yh4, 'ko', ms=6)

    # --- Annotations & Reference Lines ---
    
    # Centerlines
    ax.plot([x0, x0_f], [y0, y0_f], color='black', lw=4, alpha=0.4)
    ax.plot([x1, x2], [y1, y2], color='black', lw=4, alpha=0.4)
    ax.plot([x3, x4], [y3, y4], color='black', lw=4, alpha=0.4)
    ax.plot([x5, x6], [y5, y6], color='black', lw=4, alpha=0.4)
    ax.plot([x7, x8], [y7, y8], color='black', lw=4, alpha=0.4)

    # Reference Lines (Global Zero)
    draw_dashed_ref(ax, (x0, y0)) 
    draw_dashed_ref(ax, (x2, y2)) 
    draw_dashed_ref(ax, (x4, y4))
    draw_dashed_ref(ax, (x6, y6))
    draw_dashed_ref(ax, (x8, y8))

    # Steering Angle Reference Lines
    draw_dashed_ref(ax, (x0_f, y0_f), length=1.5, angle=theta0, color='orange')
    draw_dashed_ref(ax, (x0_f, y0_f), length=1.5, angle=theta0+delta, color='orange')

    # Drawbar 1 Reference Lines (at Dolly 1)
    # Relative angle between Trailer 1 (theta2) and Drawbar 1 (theta1)
    draw_dashed_ref(ax, (x1, y1), length=1.5, angle=theta2, color='green')
    draw_dashed_ref(ax, (x1, y1), length=1.5, angle=theta1, color='green')

    # Drawbar 2 Reference Lines (at Dolly 2)
    # Relative angle between Trailer 2 (theta4) and Drawbar 2 (theta3)
    draw_dashed_ref(ax, (x3, y3), length=1.5, angle=theta4, color='green')
    draw_dashed_ref(ax, (x3, y3), length=1.5, angle=theta3, color='green')

    # Drawbar 3 Reference Lines (at Dolly 3)
    # Relative angle between Trailer 3 (theta6) and Drawbar 3 (theta5)
    draw_dashed_ref(ax, (x5, y5), length=1.5, angle=theta6, color='green')
    draw_dashed_ref(ax, (x5, y5), length=1.5, angle=theta5, color='green')

    # Drawbar 4 Reference Lines (at Dolly 4)
    # Relative angle between Trailer 4 (theta8) and Drawbar 4 (theta7)
    draw_dashed_ref(ax, (x7, y7), length=1.5, angle=theta8, color='green')
    draw_dashed_ref(ax, (x7, y7), length=1.5, angle=theta7, color='green')
    
    # Points
    ax.text(x0-0.5, y0-0.05, '$(x_0, y_0)$', color='blue')
    ax.text(x1+0.05, y1-0.1, '$(x_1, y_1)$', color='blue')
    ax.text(x2-0.5, y2+0.05, '$(x_2, y_2)$', color='red')
    ax.text(x3-0.5, y3-0.15, '$(x_3, y_3)$', color='blue')
    ax.text(x4+0.05, y4+0.05, '$(x_4, y_4)$', color='red')
    ax.text(x5+0.1, y5-0.05, '$(x_5, y_5)$', color='blue')
    ax.text(x6+0.05, y6+0.05, '$(x_6, y_6)$', color='red')
    ax.text(x7-0.5, y7+0.05, '$(x_7, y_7)$', color='blue')
    ax.text(x8-0.52, y8+0.05, '$(x_8, y_8)$', color='red')

    # Dimensions
    ax.annotate(r'$L_0$', xy=((x0+x0_f)/2, (y0+y0_f)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_1$', xy=((xh1+x1)/2, (yh1+y1)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_2$', xy=((x1+x2)/2, (y1+y2)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_3$', xy=((xh2+x3)/2, (yh2+y3)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_4$', xy=((x3+x4)/2, (y3+y4-0.5)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_5$', xy=((xh3+x5+0.05)/2, (yh3+y5-0.5)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_6$', xy=((x5+x6)/2, (y5+y6-0.5)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_7$', xy=((xh4+x7)/2, (yh4+y7-0.5)/2), xytext=(-10, 10), textcoords='offset points')
    ax.annotate(r'$L_8$', xy=((x7+x8)/2, (y7+y8)/2), xytext=(-10, 10), textcoords='offset points')
    
    # Angles
    # Theta0
    patches.Arc((x0, y0), 3, 3, angle=0, theta1=0, theta2=np.degrees(theta0), color='blue')
    ax.text(x0+0.3, y0+0.1, r'$\theta_0$', color='blue')
    
    # Theta1
    patches.Arc((x1, y1), 3, 3, angle=0, theta1=np.degrees(theta2), theta2=np.degrees(theta1), color='green')
    ax.text(x1+0.5, y1+0.11, r'$\theta_1$', color='green')
    
    # Theta2
    patches.Arc((x2, y2), 3, 3, angle=0, theta1=0, theta2=np.degrees(theta2), color='red')
    ax.text(x2+0.8, y2+0.01, r'$\theta_2$', color='red')
    
    # Theta3
    patches.Arc((x3, y3), 3, 3, angle=0, theta1=np.degrees(theta4), theta2=np.degrees(theta3), color='green')
    ax.text(x3+0.7, y3-0.3, r'$\theta_3$', color='green')
    
    # Theta4
    patches.Arc((x4, y4), 3, 3, angle=0, theta1=0, theta2=np.degrees(theta4), color='red')
    ax.text(x4+0.5, y4-0.2, r'$\theta_4$', color='red')
    
    # Theta5
    patches.Arc((x5, y5), 3, 3, angle=0, theta1=np.degrees(theta6), theta2=np.degrees(theta5), color='green')
    ax.text(x5+0.5, y5-0.45, r'$\theta_5$', color='green')
    
    # Theta6
    patches.Arc((x6, y6), 3, 3, angle=0, theta1=0, theta2=np.degrees(theta6), color='red')
    ax.text(x6+0.5, y6-0.2, r'$\theta_6$', color='red')
    
    # Theta7
    patches.Arc((x7, y7), 3, 3, angle=0, theta1=np.degrees(theta8), theta2=np.degrees(theta7), color='green')
    ax.text(x7+0.5, y7, r'$\theta_7$', color='green')
    
    # Theta8
    patches.Arc((x8, y8), 3, 3, angle=0, theta1=0, theta2=np.degrees(theta8), color='red')
    ax.text(x8+0.5, y8+0.1, r'$\theta_8$', color='red')
    
    # Delta
    patches.Arc((x0_f, y0_f), 3, 3, angle=0, theta1=np.degrees(theta0), theta2=np.degrees(theta0+delta), color='orange')
    ax.text(x0_f+0.3, y0_f+0.5, r'$\delta$', color='orange')
    
    
    # plt.title("Kinematic Diagram: Tractor + 2 Drawbar Trailers")
    fig.suptitle("Kinematic Diagram: Tractor with Drawbar Trailers", fontsize=24, y=0.95)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path)
    print(f"Diagram saved to {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Kinematic Diagram')
    parser.add_argument('--L0', type=float, default=2.0, help='Tractor Wheelbase')
    parser.add_argument('--L1', type=float, default=1.0, help='Drawbar 1 Length')
    parser.add_argument('--L2', type=float, default=1.2, help='Trailer 1 Wheelbase')
    parser.add_argument('--L3', type=float, default=1.0, help='Drawbar 2 Length')
    parser.add_argument('--L4', type=float, default=1.2, help='Trailer 2 Wheelbase')
    parser.add_argument('--L5', type=float, default=1.0, help='Drawbar 3 Length')
    parser.add_argument('--L6', type=float, default=1.2, help='Trailer 3 Wheelbase')
    parser.add_argument('--L7', type=float, default=1.0, help='Drawbar 4 Length')
    parser.add_argument('--L8', type=float, default=1.2, help='Trailer 4 Wheelbase')
    parser.add_argument('--W', type=float, default=1.0, help='Track Width')
    parser.add_argument('--tractor_width', type=float, default=1.5, help='Tractor Body Width')
    parser.add_argument('--tractor_len', type=float, default=2.8, help='Tractor Body Length')
    parser.add_argument('--trailer_width', type=float, default=1.5, help='Trailer Body Width')
    parser.add_argument('--trailer_len', type=float, default=2.0, help='Trailer Body Length')
    parser.add_argument('--tail_ext', type=float, default=0.15, help='Tail Extension')
    
    # Angles
    parser.add_argument('--theta0', type=float, default=45.0, help='Tractor Yaw (deg)')
    parser.add_argument('--theta1', type=float, default=25.0, help='Drawbar 1 Yaw (deg)')
    parser.add_argument('--theta2', type=float, default=10.0, help='Trailer 1 Yaw (deg)')
    parser.add_argument('--theta3', type=float, default=-10.0, help='Drawbar 2 Yaw (deg)')
    parser.add_argument('--theta4', type=float, default=-25.0, help='Trailer 2 Yaw (deg)')
    parser.add_argument('--theta5', type=float, default=-45.0, help='Drawbar 3 Yaw (deg)')
    parser.add_argument('--theta6', type=float, default=-25.0, help='Trailer 3 Yaw (deg)')
    parser.add_argument('--theta7', type=float, default=-10.0, help='Drawbar 4 Yaw (deg)')
    parser.add_argument('--theta8', type=float, default=25.0, help='Trailer 4 Yaw (deg)')
    
    parser.add_argument('--save_path', type=str, default='kinematic_diagram_full.png', help='Path to save the diagram')

    args = parser.parse_args()
    
    create_diagram(L0=args.L0, L1=args.L1, L2=args.L2, L3=args.L3, L4=args.L4, 
                   L5=args.L5, L6=args.L6, L7=args.L7, L8=args.L8, W=args.W, 
                   tractor_width=args.tractor_width, tractor_len=args.tractor_len,
                   trailer_width=args.trailer_width, trailer_len=args.trailer_len, 
                   tail_ext=args.tail_ext,
                   theta0_deg=args.theta0, theta1_deg=args.theta1, theta2_deg=args.theta2,
                   theta3_deg=args.theta3, theta4_deg=args.theta4, theta5_deg=args.theta5,
                   theta6_deg=args.theta6, theta7_deg=args.theta7, theta8_deg=args.theta8,
                   save_path=args.save_path)
