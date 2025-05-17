"""
Feat Progression Path Visualization Tool

This script generates visual representations of feat progression paths
to help developers and players understand prerequisite relationships.
"""

import sys
import os
import json
from typing import Dict, List, Set
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.feats import FeatManager, PowerLevel, Feat, FeatType
from models.feat_templates import ALL_FEATS

def generate_feat_dependency_graph(output_file='feat_dependencies.png'):
    """Generate a graph visualization of feat dependencies"""
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes for all feats
    for feat_id, feat in ALL_FEATS.items():
        # Get power level value (or default)
        if hasattr(feat.prerequisites, "power_level"):
            power_level = feat.prerequisites.power_level
        else:
            power_level = PowerLevel.MEDIUM
            
        # Add node with attributes
        G.add_node(
            feat_id, 
            name=feat.name,
            power=power_level.value,  # Numeric value for coloring
            type=feat.feat_type.name,
            level=feat.prerequisites.level_requirement
        )
    
    # Add edges for feat prerequisites
    for feat_id, feat in ALL_FEATS.items():
        if feat.prerequisites.feat_requirements:
            for req_feat in feat.prerequisites.feat_requirements:
                if req_feat in ALL_FEATS:  # Ensure prerequisite exists
                    G.add_edge(req_feat, feat_id)
    
    # Create layout
    pos = nx.spring_layout(G, k=0.15, iterations=50)
    
    # Set up figure
    plt.figure(figsize=(20, 16))
    
    # Create colormap for power levels
    cmap = LinearSegmentedColormap.from_list(
        'power_cmap', ['lightblue', 'green', 'orange', 'red'], N=4
    )
    
    # Get node colors based on power level
    power_values = [G.nodes[n]['power'] for n in G.nodes()]
    
    # Draw nodes with size based on level requirement
    nx.draw_networkx_nodes(
        G, pos,
        node_color=power_values,
        cmap=cmap,
        node_size=[G.nodes[n]['level'] * 100 for n in G.nodes()],
        alpha=0.8
    )
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        arrows=True,
        width=1.5,
        alpha=0.7,
        edge_color='gray'
    )
    
    # Draw labels with smaller font
    nx.draw_networkx_labels(
        G, pos,
        labels={n: G.nodes[n]['name'] for n in G.nodes()},
        font_size=9,
        font_family='sans-serif'
    )
    
    # Add legend for power levels
    handles = [
        mpatches.Patch(color=cmap(0), label='Low Power'),
        mpatches.Patch(color=cmap(1/3), label='Medium Power'),
        mpatches.Patch(color=cmap(2/3), label='High Power'),
        mpatches.Patch(color=cmap(1), label='Very High Power')
    ]
    plt.legend(handles=handles, loc='upper right', title='Feat Power Level')
    
    # Add title and save
    plt.title('Feat Prerequisite Relationships', size=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Dependency graph saved to {output_file}")
    
    # Additional analysis
    connected_components = list(nx.weakly_connected_components(G))
    print(f"Found {len(connected_components)} separate feat progression trees")
    
    # Identify disconnected feats (not part of any progression)
    isolated_nodes = list(nx.isolates(G))
    print(f"Found {len(isolated_nodes)} isolated feats (not part of any progression)")
    
    return G

def visualize_progression_path(path_data, output_dir='progression_paths'):
    """Generate a visualization for a specific progression path"""
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    path_name = path_data['name']
    feat_ids = path_data['feats']
    
    # Create directed graph for this path
    G = nx.DiGraph()
    
    # Add nodes
    for feat_id in feat_ids:
        if feat_id in ALL_FEATS:
            feat = ALL_FEATS[feat_id]
            if hasattr(feat.prerequisites, "power_level"):
                power_level = feat.prerequisites.power_level
            else:
                power_level = PowerLevel.MEDIUM
                
            G.add_node(
                feat_id, 
                name=feat.name,
                power=power_level.value,
                type=feat.feat_type.name,
                level=feat.prerequisites.level_requirement
            )
    
    # Add edges based on prerequisites
    for i, feat_id in enumerate(feat_ids):
        if i > 0 and feat_id in ALL_FEATS and feat_ids[i-1] in ALL_FEATS:
            feat = ALL_FEATS[feat_id]
            if feat_ids[i-1] in feat.prerequisites.feat_requirements:
                G.add_edge(feat_ids[i-1], feat_id)
            else:
                # Add implied progression edge
                G.add_edge(feat_ids[i-1], feat_id, style='dashed')
    
    # Create layout - use left-to-right hierarchical layout
    pos = nx.spring_layout(G, k=0.3)
    
    # Set up figure
    plt.figure(figsize=(16, 10))
    
    # Create colormap for power levels
    cmap = LinearSegmentedColormap.from_list(
        'power_cmap', ['lightblue', 'green', 'orange', 'red'], N=4
    )
    
    # Get node colors based on power level
    power_values = [G.nodes[n]['power'] for n in G.nodes()]
    
    # Draw nodes with size based on level requirement
    nx.draw_networkx_nodes(
        G, pos,
        node_color=power_values,
        cmap=cmap,
        node_size=[G.nodes[n]['level'] * 150 for n in G.nodes()],
        alpha=0.8
    )
    
    # Draw edges - solid for explicit prerequisites, dashed for implied progression
    solid_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('style', 'solid') == 'solid']
    dashed_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('style') == 'dashed']
    
    nx.draw_networkx_edges(
        G, pos,
        edgelist=solid_edges,
        arrows=True,
        width=2.0,
        alpha=0.8,
        edge_color='black'
    )
    
    nx.draw_networkx_edges(
        G, pos,
        edgelist=dashed_edges,
        arrows=True,
        width=1.5,
        alpha=0.6,
        edge_color='gray',
        style='dashed'
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        labels={n: f"{G.nodes[n]['name']}\nLevel {G.nodes[n]['level']}" for n in G.nodes()},
        font_size=11,
        font_family='sans-serif'
    )
    
    # Add legend for power levels
    handles = [
        mpatches.Patch(color=cmap(0), label='Low Power'),
        mpatches.Patch(color=cmap(1/3), label='Medium Power'),
        mpatches.Patch(color=cmap(2/3), label='High Power'),
        mpatches.Patch(color=cmap(1), label='Very High Power')
    ]
    
    # Add legend for edge types
    handles.extend([
        mpatches.Patch(color='black', label='Explicit Prerequisite'),
        mpatches.Patch(color='gray', label='Implied Progression')
    ])
    
    plt.legend(handles=handles, loc='upper right')
    
    # Add title and save
    plt.title(f'Feat Progression Path: {path_name}', size=16)
    plt.axis('off')
    plt.tight_layout()
    
    # Use sanitized path name for filename
    filename = path_name.lower().replace(' ', '_').replace('/', '_')
    output_file = os.path.join(output_dir, f"{filename}.png")
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"Path visualization saved to {output_file}")
    
    # Get additional path information for report
    path_info = {
        "name": path_name,
        "description": path_data['description'],
        "feat_count": len(feat_ids),
        "level_range": (
            min(ALL_FEATS[f].prerequisites.level_requirement for f in feat_ids if f in ALL_FEATS),
            max(ALL_FEATS[f].prerequisites.level_requirement for f in feat_ids if f in ALL_FEATS)
        ),
        "feats": [
            {
                "id": f,
                "name": ALL_FEATS[f].name if f in ALL_FEATS else "Unknown",
                "level": ALL_FEATS[f].prerequisites.level_requirement if f in ALL_FEATS else 0,
                "type": ALL_FEATS[f].feat_type.name if f in ALL_FEATS else "Unknown",
            }
            for f in feat_ids
        ]
    }
    
    return path_info

def visualize_all_progression_paths(paths_file='suggested_paths.json', output_dir='progression_paths'):
    """Visualize all progression paths from a JSON file"""
    
    # Load paths data
    with open(paths_file, 'r') as f:
        paths_data = json.load(f)
    
    path_reports = []
    
    # Visualize each path
    for path in paths_data:
        path_info = visualize_progression_path(path, output_dir)
        path_reports.append(path_info)
    
    # Generate HTML report
    generate_html_report(path_reports, output_dir)
    
    return path_reports

def generate_html_report(path_reports, output_dir):
    """Generate an HTML report of all progression paths"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feat Progression Paths</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .path { margin-bottom: 30px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .path-header { display: flex; justify-content: space-between; align-items: center; }
            .path-header h2 { margin: 0; }
            .level-range { color: #666; }
            .path-image { margin-top: 20px; max-width: 100%; height: auto; }
            .feat-list { margin-top: 20px; }
            .feat { padding: 10px; margin: 5px 0; background-color: #f5f5f5; border-radius: 3px; }
            .feat-name { font-weight: bold; }
            .feat-details { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>Feat Progression Paths</h1>
    """
    
    for path in path_reports:
        # Use sanitized path name for filename
        filename = path['name'].lower().replace(' ', '_').replace('/', '_')
        
        html_content += f"""
        <div class="path">
            <div class="path-header">
                <h2>{path['name']}</h2>
                <span class="level-range">Levels {path['level_range'][0]} - {path['level_range'][1]}</span>
            </div>
            <p>{path['description']}</p>
            <img class="path-image" src="{filename}.png" alt="{path['name']} visualization" />
            
            <div class="feat-list">
                <h3>Feats in this Progression:</h3>
        """
        
        for feat in path['feats']:
            html_content += f"""
                <div class="feat">
                    <div class="feat-name">{feat['name']} (ID: {feat['id']})</div>
                    <div class="feat-details">Level Requirement: {feat['level']} | Type: {feat['type']}</div>
                </div>
            """
        
        html_content += """
            </div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    # Write HTML report
    with open(os.path.join(output_dir, 'progression_paths_report.html'), 'w') as f:
        f.write(html_content)
    
    print(f"HTML report saved to {os.path.join(output_dir, 'progression_paths_report.html')}")

if __name__ == "__main__":
    print("Generating feat dependency graph...")
    G = generate_feat_dependency_graph()
    
    if os.path.exists('suggested_paths.json'):
        print("\nVisualizing progression paths...")
        visualize_all_progression_paths()
    else:
        print("\nNo suggested_paths.json file found. Run analyze_feats.py first to generate suggested paths.")
    
    print("\nVisualization complete!") 