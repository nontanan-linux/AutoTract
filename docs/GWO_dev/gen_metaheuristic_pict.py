import matplotlib.pyplot as plt

def create_classification_diagram():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Define node positions (x, y)
    positions = {
        'root': (0.5, 0.9),
        'evolutionary': (0.15, 0.7),
        'physics': (0.38, 0.7),
        'swarm': (0.62, 0.7),
        'human': (0.85, 0.7),
        
        # Examples
        'ga': (0.15, 0.55),
        'de': (0.15, 0.5),
        
        'gsa': (0.38, 0.55),
        'sa': (0.38, 0.5),
        
        'pso': (0.62, 0.55),
        'gwo': (0.62, 0.5),
        'aco': (0.62, 0.45),
        
        'tlbo': (0.85, 0.55),
        'ica': (0.85, 0.5)
    }

    labels = {
        'root': 'Meta-heuristic\nAlgorithms',
        'evolutionary': 'Evolutionary\nAlgorithms',
        'physics': 'Physics-based\nAlgorithms',
        'swarm': 'Swarm-based\nAlgorithms',
        'human': 'Human-based\nAlgorithms',
        
        'ga': 'GA (Genetic Alg.)',
        'de': 'DE (Differential Evol.)',
        
        'gsa': 'GSA (Gravitational Search)',
        'sa': 'SA (Simulated Annealing)',
        
        'pso': 'PSO (Particle Swarm)',
        'gwo': 'GWO (Grey Wolf)',
        'aco': 'ACO (Ant Colony)',
        
        'tlbo': 'TLBO (Teaching-Learning)',
        'ica': 'ICA (Imperialist Comp.)'
    }

    # Draw edges
    connections = [
        ('root', 'evolutionary'),
        ('root', 'physics'),
        ('root', 'swarm'),
        ('root', 'human'),
        
        ('evolutionary', 'ga'),
        ('evolutionary', 'de'),
        
        ('physics', 'gsa'),
        ('physics', 'sa'),
        
        ('swarm', 'pso'),
        ('swarm', 'gwo'),
        ('swarm', 'aco'),
        
        ('human', 'tlbo'),
        ('human', 'ica')
    ]

    for start, end in connections:
        start_pos = positions[start]
        end_pos = positions[end]
        # Draw line, but leave some space for text boxes
        ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 'k-', zorder=1)

    # Draw nodes
    for key, pos in positions.items():
        x, y = pos
        label = labels[key]
        
        # Style based on level
        if key == 'root':
            bbox_props = dict(boxstyle="round,pad=0.5", fc="lightgray", ec="black", lw=2)
            fontsize = 12
            fontweight = 'bold'
        elif key in ['evolutionary', 'physics', 'swarm', 'human']:
            bbox_props = dict(boxstyle="round,pad=0.5", fc="lightblue", ec="blue", lw=1.5)
            fontsize = 10
            fontweight = 'bold'
        else:
            bbox_props = dict(boxstyle="square,pad=0.3", fc="white", ec="gray", lw=1)
            fontsize = 9
            fontweight = 'normal'

        ax.text(x, y, label, ha='center', va='center', bbox=bbox_props, fontsize=fontsize, fontweight=fontweight, zorder=2)

    plt.title('Figure 1: Classification of Meta-heuristic Algorithms', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig('pict/Figure1_Classification.png', dpi=300)
    print("Generated pict/Figure1_Classification.png")

if __name__ == "__main__":
    create_classification_diagram()
