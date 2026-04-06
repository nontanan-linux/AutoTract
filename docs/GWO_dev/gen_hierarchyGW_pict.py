import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_hierarchy_diagram():
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Triangle vertices
    top = (5, 9)
    left = (2, 1)
    right = (8, 1)

    # Function to interpolate points on the triangle edges
    def get_points(level_ratio_top, level_ratio_bottom):
        # Left edge interpolation
        l_x_top = top[0] + (left[0] - top[0]) * level_ratio_top
        l_y_top = top[1] + (left[1] - top[1]) * level_ratio_top
        
        l_x_bot = top[0] + (left[0] - top[0]) * level_ratio_bottom
        l_y_bot = top[1] + (left[1] - top[1]) * level_ratio_bottom
        
        # Right edge interpolation
        r_x_top = top[0] + (right[0] - top[0]) * level_ratio_top
        r_y_top = top[1] + (right[1] - top[1]) * level_ratio_top
        
        r_x_bot = top[0] + (right[0] - top[0]) * level_ratio_bottom
        r_y_bot = top[1] + (right[1] - top[1]) * level_ratio_bottom
        
        return [(l_x_top, l_y_top), (r_x_top, r_y_top), (r_x_bot, r_y_bot), (l_x_bot, l_y_bot)]

    # Draw layers
    alpha_verts = get_points(0.0, 0.25)
    beta_verts = get_points(0.25, 0.50)
    delta_verts = get_points(0.50, 0.75)
    omega_verts = get_points(0.75, 1.0)

    colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#A9A9A9'] # Gold, Silver, Bronze, DarkGray
    labels = [r'$\alpha$ (Alpha)', r'$\beta$ (Beta)', r'$\delta$ (Delta)', r'$\omega$ (Omega)']
    descriptions = [
        "Leaders / Decision Makers",
        "Subvisors / Advisors",
        "Scouts / Sentinels / Elders",
        "Scapegoats / Followers"
    ]

    for i, (verts, color, label, desc) in enumerate(zip([alpha_verts, beta_verts, delta_verts, omega_verts], colors, labels, descriptions)):
        poly = patches.Polygon(verts, closed=True, edgecolor='black', facecolor=color, alpha=0.8)
        ax.add_patch(poly)
        
        # Add labels
        center_y = (verts[0][1] + verts[3][1]) / 2
        ax.text(5, center_y, label, ha='center', va='center', fontsize=14, fontweight='bold')
        
        # Add description on the right
        ax.text(8.2, center_y, desc, ha='left', va='center', fontsize=10, style='italic')

    plt.title('Figure 2: Social Hierarchy of Grey Wolves', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig('pict/Figure2_SocialHierarchy.png', dpi=300)
    print("Generated pict/Figure2_SocialHierarchy.png")

if __name__ == "__main__":
    create_hierarchy_diagram()
