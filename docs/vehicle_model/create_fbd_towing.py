import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Parameters (Must match create_diagram.py exactly)
L0 = 2.0                   # Tractor wheelbase
L1 = 1.0                   # Drawbar 1 length
L2 = 1.2                   # Trailer 1 wheelbase
tractor_width = 1.5
tractor_len = 2.8
trailer_width = 1.5
trailer_len = 2.0
tail_ext = 0.15
W = 1.5                    # Track width

# Drawing scale adjustment to enclose wheels (matching vehicle_reference_frames.png style)
chassis_draw_width = 1.3 * W  # 1.95, which completely encloses the wheels (outer wheel edge is at W/2 + wheel_width/2 = 0.9)

tractor_overhang = (tractor_len - L0) / 2
dh = tractor_overhang + tail_ext 
trailer_overhang = (trailer_len - L2) / 2

# Angles (Must match create_diagram.py default angles)
theta0 = np.radians(45.0)  # Tractor Yaw
theta1 = np.radians(25.0)  # Drawbar/Dolly Yaw
theta2 = np.radians(10.0)  # Trailer Yaw
delta = np.radians(25.0)   # Tractor steering angle

# Wheel Dimensions
r_wheel = 10 * 0.0254
wheel_diam = 2 * r_wheel
wheel_width = 0.3

# Helper function to draw a wheel pair (from create_diagram.py)
def draw_wheel_pair(ax, center, angle, width, steered_angle=0, color='#7f8c8d', alpha=0.6):
    cx, cy = center
    px = -np.sin(angle)
    py = np.cos(angle)
    
    wl_x = cx + (width/2) * px
    wl_y = cy + (width/2) * py
    wr_x = cx - (width/2) * px
    wr_y = cy - (width/2) * py
    
    ax.plot([wl_x, wr_x], [wl_y, wr_y], 'k-', lw=1.5, zorder=2)
    
    wa = angle + steered_angle
    
    for wx, wy in [(wl_x, wl_y), (wr_x, wr_y)]:
        c, s = np.cos(wa), np.sin(wa)
        dx, dy = -wheel_diam/2, -wheel_width/2
        rx = dx*c - dy*s
        ry = dx*s + dy*c
        rect = patches.Rectangle((wx+rx, wy+ry), wheel_diam, wheel_width, angle=np.degrees(wa), 
                                 facecolor=color, edgecolor='#2c3e50', linewidth=1.0, zorder=3, alpha=alpha)
        ax.add_patch(rect)

# Helper function to draw a chassis box (from create_diagram.py)
def draw_chassis(ax, center, length, width, angle, color='gray', alpha=0.25):
    cx, cy = center
    c, s = np.cos(angle), np.sin(angle)
    dx, dy = -length/2, -width/2
    rx = dx*c - dy*s
    ry = dx*s + dy*c
    rect = patches.Rectangle((cx+rx, cy+ry), length, width, angle=np.degrees(angle), 
                             linewidth=1.5, edgecolor='black', facecolor=color, alpha=alpha, zorder=1)
    ax.add_patch(rect)


# =========================================================================
# 1. TRACTOR FBD (vehicle_fbd_tractor.png)
# =========================================================================
fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
ax.set_aspect('equal')
ax.set_xlim(0.5, 6.5)
ax.set_ylim(0.5, 7.0)
ax.axis('off')

cg0 = np.array([3.5, 3.8])
u_long0 = np.array([np.cos(theta0), np.sin(theta0)])
u_lat0 = np.array([-np.sin(theta0), np.cos(theta0)])

F0 = cg0 + (L0 / 2.0) * u_long0
R0 = cg0 - (L0 / 2.0) * u_long0
hitch1 = R0 - dh * u_long0

# Draw Tractor Body (chassis_draw_width is used here to enclose wheels)
p_tr_front_face = F0 + tractor_overhang * u_long0
p_tr_rear_face = R0 - tractor_overhang * u_long0
p_tr_c = (p_tr_front_face + p_tr_rear_face) / 2
draw_chassis(ax, p_tr_c, tractor_len, chassis_draw_width, theta0, color='orangered', alpha=0.25)

# Wheels
draw_wheel_pair(ax, F0, theta0, W, steered_angle=delta)
draw_wheel_pair(ax, R0, theta0, W)

# Centerline
ax.plot([p_tr_rear_face[0], p_tr_front_face[0]], [p_tr_rear_face[1], p_tr_front_face[1]], 'k-.', lw=1, alpha=0.5, zorder=2)
ax.plot([p_tr_rear_face[0], hitch1[0]], [p_tr_rear_face[1], hitch1[1]], 'k-', lw=1.5, zorder=2)

# C.G. and Hitch markers
cg_circle = patches.Circle(cg0, radius=0.12, edgecolor='black', facecolor='none', linewidth=1.2, zorder=6)
ax.add_patch(cg_circle)
ax.add_patch(patches.Wedge(cg0, r=0.12, theta1=np.degrees(theta0), theta2=np.degrees(theta0)+90, color='black', zorder=5))
ax.add_patch(patches.Wedge(cg0, r=0.12, theta1=np.degrees(theta0)+180, theta2=np.degrees(theta0)+270, color='black', zorder=5))
ax.text(cg0[0]-0.25, cg0[1]-0.35, '$C.G._0$', fontsize=10, fontweight='bold')

hitch_circle1 = patches.Circle(hitch1, radius=0.08, edgecolor='black', facecolor='black', zorder=5)
ax.add_patch(hitch_circle1)
ax.text(hitch1[0]-0.3, hitch1[1]-0.3, '$H_1$', fontsize=10, fontweight='bold')

# --- Dimension Lines (Tractor) ---
dim_offset = -1.2 * u_lat0
cg_proj = cg0 + dim_offset
rear_proj = R0 + dim_offset
front_proj = F0 + dim_offset

dim_offset_dh = -1.7 * u_lat0
cg_proj_dh = cg0 + dim_offset_dh
hitch_proj_dh = hitch1 + dim_offset_dh

# Extension lines (thin dotted)
ax.plot([cg0[0], cg_proj[0]], [cg0[1], cg_proj[1]], color='#95a5a6', linestyle=':', lw=1)
ax.plot([R0[0], rear_proj[0]], [R0[1], rear_proj[1]], color='#95a5a6', linestyle=':', lw=1)
ax.plot([F0[0], front_proj[0]], [F0[1], front_proj[1]], color='#95a5a6', linestyle=':', lw=1)
ax.plot([cg0[0], cg_proj_dh[0]], [cg0[1], cg_proj_dh[1]], color='#95a5a6', linestyle=':', lw=1)
ax.plot([hitch1[0], hitch_proj_dh[0]], [hitch1[1], hitch_proj_dh[1]], color='#95a5a6', linestyle=':', lw=1)

# Dimension double arrows
ax.annotate('', xy=front_proj, xytext=cg_proj, arrowprops=dict(arrowstyle="<->", color='#7f8c8d', lw=1.2), zorder=2)
ax.annotate('', xy=rear_proj, xytext=cg_proj, arrowprops=dict(arrowstyle="<->", color='#7f8c8d', lw=1.2), zorder=2)
ax.annotate('', xy=hitch_proj_dh, xytext=cg_proj_dh, arrowprops=dict(arrowstyle="<->", color='#7f8c8d', lw=1.2), zorder=2)

# Dimension Labels
lf_label_pos = cg_proj + 0.5 * (L0/2.0) * u_long0 - 0.25 * u_lat0
lr_label_pos = cg_proj - 0.5 * (L0/2.0) * u_long0 - 0.25 * u_lat0
dh_label_pos = cg_proj_dh - 0.5 * (L0/2.0 + dh) * u_long0 - 0.25 * u_lat0

ax.text(lf_label_pos[0], lf_label_pos[1], '$l_f$', fontsize=11, color='#7f8c8d', ha='center', va='center')
ax.text(lr_label_pos[0], lr_label_pos[1], '$l_r$', fontsize=11, color='#7f8c8d', ha='center', va='center')
ax.text(dh_label_pos[0], dh_label_pos[1], '$d_h$', fontsize=11, color='#7f8c8d', ha='center', va='center')

# Force arrows (Tractor FBD)
force_arrow = dict(arrowstyle="->", color='#e74c3c', lw=2.5, mutation_scale=15)
hitch_arrow1 = dict(arrowstyle="->", color='#8e44ad', lw=2.5, mutation_scale=15)

# Front tire forces (along steered wheel direction)
w_long0 = np.array([np.cos(theta0+delta), np.sin(theta0+delta)])
w_lat0 = np.array([-np.sin(theta0+delta), np.cos(theta0+delta)])
ax.annotate('', xy=F0 + 1.2*w_long0, xytext=F0, arrowprops=force_arrow, zorder=5)
ax.text((F0 + 1.3*w_long0)[0], (F0 + 1.3*w_long0)[1], '$F_{xf}$', color='#e74c3c', fontsize=12, fontweight='bold')
ax.annotate('', xy=F0 + 1.0*w_lat0, xytext=F0, arrowprops=force_arrow, zorder=5)
ax.text((F0 + 1.1*w_lat0)[0], (F0 + 1.1*w_lat0)[1], '$F_{yf}$', color='#e74c3c', fontsize=12, fontweight='bold')

# Rear tire forces
ax.annotate('', xy=R0 + 1.2*u_long0, xytext=R0, arrowprops=force_arrow, zorder=5)
ax.text((R0 + 1.3*u_long0)[0], (R0 + 1.3*u_long0)[1], '$F_{xr}$', color='#e74c3c', fontsize=12, fontweight='bold')
ax.annotate('', xy=R0 + 1.0*u_lat0, xytext=R0, arrowprops=force_arrow, zorder=5)
ax.text((R0 + 1.1*u_lat0)[0], (R0 + 1.1*u_lat0)[1], '$F_{yr}$', color='#e74c3c', fontsize=12, fontweight='bold')

# Hitch forces acting ON Tractor
ax.annotate('', xy=hitch1 - 1.2*u_long0, xytext=hitch1, arrowprops=hitch_arrow1, zorder=5)
ax.text((hitch1 - 1.4*u_long0)[0], (hitch1 - 1.4*u_long0)[1], '$F_{hx1}$', color='#8e44ad', fontsize=12, fontweight='bold')
ax.annotate('', xy=hitch1 + 1.0*u_lat0, xytext=hitch1, arrowprops=hitch_arrow1, zorder=5)
ax.text((hitch1 + 1.1*u_lat0)[0], (hitch1 + 1.1*u_lat0)[1], '$F_{hy1}$', color='#8e44ad', fontsize=12, fontweight='bold')

ax.set_title('Free Body Diagram: Towing Vehicle (Tractor)', fontsize=14, fontweight='bold')
plt.savefig('/home/robinz/AutoTract/docs/vehicle_model/vehicle_fbd_tractor.png', bbox_inches='tight', pad_inches=0.1)
plt.close()


# =========================================================================
# 2. DRAWBAR TRAILER FBD (vehicle_fbd_trailer.png)
# =========================================================================
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
ax.set_aspect('equal')
ax.set_xlim(1.5, 7.5)
ax.set_ylim(1.0, 5.5)
ax.axis('off')

dolly_center = np.array([4.5, 3.2])
u_long1 = np.array([np.cos(theta1), np.sin(theta1)])
u_lat1 = np.array([-np.sin(theta1), np.cos(theta1)])

# Dolly and Drawbar coordinates
hitch1_offset = dolly_center + L1 * u_long1

# Trailer coordinates (drawn connected to dolly_center)
trailer_rear = dolly_center - L2 * np.array([np.cos(theta2), np.sin(theta2)])
cg2 = dolly_center - (L2 / 2.0) * np.array([np.cos(theta2), np.sin(theta2)])

u_long2 = np.array([np.cos(theta2), np.sin(theta2)])
u_lat2 = np.array([-np.sin(theta2), np.cos(theta2)])

# Draw Trailer Body (Chassis box centered at the midpoint of dolly and rear axles, rotated by theta2)
# chassis_draw_width is used here to enclose wheels
p_tl_front_face = dolly_center + trailer_overhang * u_long2
p_tl_rear_face = trailer_rear - trailer_overhang * u_long2
p_tl_c = (p_tl_front_face + p_tl_rear_face) / 2
draw_chassis(ax, p_tl_c, trailer_len, chassis_draw_width, theta2, color='blue', alpha=0.15)

# Draw Drawbar link (from drawbar eye H1' to dolly axle center)
ax.plot([hitch1_offset[0], dolly_center[0]], [hitch1_offset[1], dolly_center[1]], 'k-', lw=3, zorder=2)

# Draw Dolly Wheels and Trailer Rear Wheels
draw_wheel_pair(ax, dolly_center, theta1, W)
draw_wheel_pair(ax, trailer_rear, theta2, W)

# Trailer Centerline
ax.plot([trailer_rear[0] - 0.4*u_long2[0], dolly_center[0] + 0.4*u_long2[0]], 
        [trailer_rear[1] - 0.4*u_long2[1], dolly_center[1] + 0.4*u_long2[1]], 'k-.', lw=1, alpha=0.5, zorder=2)

# Joints and C.G. markers
hitch_offset_circle = patches.Circle(hitch1_offset, radius=0.08, edgecolor='black', facecolor='black', zorder=5)
ax.add_patch(hitch_offset_circle)
ax.text(hitch1_offset[0]-0.3, hitch1_offset[1]-0.3, "$H_1'$", fontsize=10, fontweight='bold')

dolly_circle = patches.Circle(dolly_center, radius=0.08, edgecolor='black', facecolor='black', zorder=5)
ax.add_patch(dolly_circle)
ax.text(dolly_center[0]-0.3, dolly_center[1]-0.35, '$H_2$', fontsize=10, fontweight='bold')

cg2_circle = patches.Circle(cg2, radius=0.12, edgecolor='black', facecolor='none', linewidth=1.2, zorder=6)
ax.add_patch(cg2_circle)
ax.add_patch(patches.Wedge(cg2, r=0.12, theta1=np.degrees(theta2), theta2=np.degrees(theta2)+90, color='black', zorder=5))
ax.add_patch(patches.Wedge(cg2, r=0.12, theta1=np.degrees(theta2)+180, theta2=np.degrees(theta2)+270, color='black', zorder=5))
ax.text(cg2[0]-0.25, cg2[1]-0.35, '$C.G._2$', fontsize=10, fontweight='bold')

# --- Dimension Lines (Trailer) ---
dim_offset = -1.2 * u_lat2
hitch_proj = hitch1_offset + dim_offset
dolly_proj = dolly_center + dim_offset
rear_proj = trailer_rear + dim_offset

# Extension lines (thin dotted)
ax.plot([hitch1_offset[0], hitch_proj[0]], [hitch1_offset[1], hitch_proj[1]], color='#95a5a6', linestyle=':', lw=1)
ax.plot([dolly_center[0], dolly_proj[0]], [dolly_center[1], dolly_proj[1]], color='#95a5a6', linestyle=':', lw=1)
ax.plot([trailer_rear[0], rear_proj[0]], [trailer_rear[1], rear_proj[1]], color='#95a5a6', linestyle=':', lw=1)

# Dimension double arrows
ax.annotate('', xy=hitch_proj, xytext=dolly_proj, arrowprops=dict(arrowstyle="<->", color='#7f8c8d', lw=1.2), zorder=2)
ax.annotate('', xy=dolly_proj, xytext=rear_proj, arrowprops=dict(arrowstyle="<->", color='#7f8c8d', lw=1.2), zorder=2)

# Dimension Labels
L1_label_pos = 0.5 * (hitch_proj + dolly_proj) - 0.25 * u_lat2
L2_label_pos = 0.5 * (dolly_proj + rear_proj) - 0.25 * u_lat2

ax.text(L1_label_pos[0], L1_label_pos[1], '$L_1$', fontsize=11, color='#7f8c8d', ha='center', va='center')
ax.text(L2_label_pos[0], L2_label_pos[1], '$L_2$', fontsize=11, color='#7f8c8d', ha='center', va='center')

# Forces on Trailer FBD
# Joint H1' reaction forces acting ON Drawbar (from Tractor)
ax.annotate('', xy=hitch1_offset + 1.2*u_long0, xytext=hitch1_offset, arrowprops=hitch_arrow1, zorder=5)
ax.text((hitch1_offset + 1.3*u_long0)[0], (hitch1_offset + 1.3*u_long0)[1], '$-F_{hx1}$', color='#8e44ad', fontsize=12, fontweight='bold')
ax.annotate('', xy=hitch1_offset - 1.0*u_lat0, xytext=hitch1_offset, arrowprops=hitch_arrow1, zorder=5)
ax.text((hitch1_offset - 1.2*u_lat0)[0], (hitch1_offset - 1.2*u_lat0)[1], '$-F_{hy1}$', color='#8e44ad', fontsize=12, fontweight='bold')

# Dolly tire forces (at dolly center)
ax.annotate('', xy=dolly_center + 1.2*u_long1, xytext=dolly_center, arrowprops=force_arrow, zorder=5)
ax.text((dolly_center + 1.3*u_long1)[0], (dolly_center + 1.3*u_long1)[1], '$F_{xd}$', color='#e74c3c', fontsize=12, fontweight='bold')
ax.annotate('', xy=dolly_center + 1.0*u_lat1, xytext=dolly_center, arrowprops=force_arrow, zorder=5)
ax.text((dolly_center + 1.1*u_lat1)[0], (dolly_center + 1.1*u_lat1)[1], '$F_{yd}$', color='#e74c3c', fontsize=12, fontweight='bold')

# Trailer rear tire forces (at trailer rear)
ax.annotate('', xy=trailer_rear + 1.2*u_long2, xytext=trailer_rear, arrowprops=force_arrow, zorder=5)
ax.text((trailer_rear + 1.3*u_long2)[0], (trailer_rear + 1.3*u_long2)[1], '$F_{xt}$', color='#e74c3c', fontsize=12, fontweight='bold')
ax.annotate('', xy=trailer_rear + 1.0*u_lat2, xytext=trailer_rear, arrowprops=force_arrow, zorder=5)
ax.text((trailer_rear + 1.1*u_lat2)[0], (trailer_rear + 1.1*u_lat2)[1], '$F_{yt}$', color='#e74c3c', fontsize=12, fontweight='bold')

ax.text(cg2[0] + 0.3*u_lat2[0], cg2[1] + 1.2*u_lat2[1], 'Drawbar Trailer', fontsize=13, color='blue', fontweight='bold', ha='center')

ax.set_title('Free Body Diagram: Drawbar Trailer (Dolly + Trailer Body)', fontsize=14, fontweight='bold')
plt.savefig('/home/robinz/AutoTract/docs/vehicle_model/vehicle_fbd_trailer.png', bbox_inches='tight', pad_inches=0.1)
plt.close()

print("Both FBD diagrams updated with enclosed wheels!")
