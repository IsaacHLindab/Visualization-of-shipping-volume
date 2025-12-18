"""3D visualization functions for truck loading"""

import plotly.graph_objects as go
import numpy as np
from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT, DEFAULT_CAMERA
from utils.geometry import rotate_dimensions, calculate_totals


def create_box_mesh(x, y, z, width, height, depth, color, name, weight, rotation):
    """Create a 3D box mesh for a package"""
    # Adjust dimensions based on rotation
    actual_width, actual_height = rotate_dimensions(width, height, rotation)
    
    # Define the 8 vertices of the box
    vertices = np.array([
        [x, y, z],
        [x + actual_width, y, z],
        [x + actual_width, y + actual_height, z],
        [x, y + actual_height, z],
        [x, y, z + depth],
        [x + actual_width, y, z + depth],
        [x + actual_width, y + actual_height, z + depth],
        [x, y + actual_height, z + depth]
    ])
    
    # Define the 6 faces (each face is 2 triangles)
    i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 0, 0, 1, 1, 2, 2, 3, 3]
    j = [1, 3, 2, 0, 3, 1, 0, 2, 5, 7, 6, 4, 7, 5, 4, 6, 4, 3, 5, 0, 6, 1, 7, 2]
    k = [2, 2, 6, 5, 6, 6, 7, 7, 6, 6, 7, 7, 3, 3, 0, 0, 7, 7, 6, 4, 7, 5, 4, 6]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=0.8,
        name=name,
        hovertemplate=f'<b>{name}</b><br>' +
                      f'Position: ({x:.1f}, {y:.1f}, {z:.1f})<br>' +
                      f'Size: {actual_width:.1f} × {actual_height:.1f} × {depth:.1f}m<br>' +
                      f'Weight: {weight} kg<br>' +
                      f'Rotation: {rotation}°<br>' +
                      '<extra></extra>',
        showlegend=True
    )


def create_truck_wireframe():
    """Create wireframe for truck trailer"""
    edges_x = []
    edges_y = []
    edges_z = []
    
    bottom_rect = [
        [0, 0, 0], [TRUCK_LENGTH, 0, 0],
        [TRUCK_LENGTH, 0, 0], [TRUCK_LENGTH, TRUCK_WIDTH, 0],
        [TRUCK_LENGTH, TRUCK_WIDTH, 0], [0, TRUCK_WIDTH, 0],
        [0, TRUCK_WIDTH, 0], [0, 0, 0]
    ]
    
    top_rect = [
        [0, 0, TRUCK_HEIGHT], [TRUCK_LENGTH, 0, TRUCK_HEIGHT],
        [TRUCK_LENGTH, 0, TRUCK_HEIGHT], [TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT],
        [TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT], [0, TRUCK_WIDTH, TRUCK_HEIGHT],
        [0, TRUCK_WIDTH, TRUCK_HEIGHT], [0, 0, TRUCK_HEIGHT]
    ]
    
    vertical = [
        [0, 0, 0], [0, 0, TRUCK_HEIGHT],
        [TRUCK_LENGTH, 0, 0], [TRUCK_LENGTH, 0, TRUCK_HEIGHT],
        [TRUCK_LENGTH, TRUCK_WIDTH, 0], [TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT],
        [0, TRUCK_WIDTH, 0], [0, TRUCK_WIDTH, TRUCK_HEIGHT]
    ]
    
    all_edges = bottom_rect + top_rect + vertical
    
    for i in range(0, len(all_edges), 2):
        edges_x.extend([all_edges[i][0], all_edges[i+1][0], None])
        edges_y.extend([all_edges[i][1], all_edges[i+1][1], None])
        edges_z.extend([all_edges[i][2], all_edges[i+1][2], None])
    
    return go.Scatter3d(
        x=edges_x, y=edges_y, z=edges_z,
        mode='lines',
        line=dict(color='gray', width=3),
        name='Truck Trailer',
        hoverinfo='skip',
        showlegend=True
    )


def create_truck_floor():
    return go.Mesh3d(
        x=[0, TRUCK_LENGTH, TRUCK_LENGTH, 0],
        y=[0, 0, TRUCK_WIDTH, TRUCK_WIDTH],
        z=[0, 0, 0, 0],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color='lightgray',
        opacity=0.2,
        name='Floor',
        hoverinfo='skip',
        showlegend=False
    )


def create_figure(packages, camera=None):
    """
    Create the 3D figure with truck and packages
    
    Args:
        packages: List of package dictionaries
        camera: Optional camera position dict
    
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Add truck wireframe and floor
    fig.add_trace(create_truck_wireframe())
    fig.add_trace(create_truck_floor())
    
    # Add all packages
    for pkg in packages:
        fig.add_trace(create_box_mesh(
            pkg['x'], pkg['y'], pkg['z'],
            pkg['width'], pkg['height'], pkg['depth'],
            pkg['color'], pkg['name'], pkg['weight'], pkg.get('rotation', 0)
        ))
    
    total_weight, total_volume = calculate_totals(packages)
    truck_volume = TRUCK_LENGTH * TRUCK_WIDTH * TRUCK_HEIGHT
    load_rate = (total_volume / truck_volume) * 100

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Length (m)', range=[0, TRUCK_LENGTH]),
            yaxis=dict(title='Width (m)', range=[0, TRUCK_WIDTH]),
            zaxis=dict(title='Height (m)', range=[0, TRUCK_HEIGHT]),
            aspectmode='data',
            camera=camera if camera else DEFAULT_CAMERA
        ),
        title=dict(
            text=f'3D Truck Loading Visualization - {len(packages)} Package(s)',
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='#1e293b',
        plot_bgcolor='#1e293b',
        font=dict(color='white')
    )
    
    return fig


# Custom / changing the truck dims by input fields
def create_figure_custom(packages, camera=None, truck_dims=None):
    """
    Create 3D figure with custom truck dimensions
    
    Args:
        packages: List of package dictionaries
        camera: Optional camera position dict
        truck_dims: Dict with 'length', 'width', 'height'
    """
    # Use custom dimensions or defaults
    if truck_dims:
        truck_length = truck_dims['length']
        truck_width = truck_dims['width']
        truck_height = truck_dims['height']
    else:
        truck_length = TRUCK_LENGTH
        truck_width = TRUCK_WIDTH
        truck_height = TRUCK_HEIGHT
    
    fig = go.Figure()
    
    # Add truck wireframe with custom dimensions
    fig.add_trace(create_truck_wireframe_custom(truck_length, truck_width, truck_height))
    fig.add_trace(create_truck_floor_custom(truck_length, truck_width))
    
    # Add packages
    for pkg in packages:
        fig.add_trace(create_box_mesh(
            pkg['x'], pkg['y'], pkg['z'],
            pkg['width'], pkg['height'], pkg['depth'],
            pkg['color'], pkg['name'], pkg['weight'], pkg.get('rotation', 0)
        ))
    
    total_weight, total_volume = calculate_totals(packages)
    truck_volume = truck_length * truck_width * truck_height
    load_rate = (total_volume / truck_volume) * 100

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Length (m)', range=[0, truck_length]),
            yaxis=dict(title='Width (m)', range=[0, truck_width]),
            zaxis=dict(title='Height (m)', range=[0, truck_height]),
            aspectmode='data',
            camera=camera if camera else DEFAULT_CAMERA
        ),
        title=dict(
            text=f'3D Truck Loading ({truck_length}x{truck_width}x{truck_height}m) - {len(packages)} Package(s)',
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='#1e293b',
        plot_bgcolor='#1e293b',
        font=dict(color='white')
    )
    
    return fig


def create_truck_wireframe_custom(length, width, height):
    """Create wireframe with custom dimensions"""
    edges_x = []
    edges_y = []
    edges_z = []
    
    bottom_rect = [
        [0, 0, 0], [length, 0, 0],
        [length, 0, 0], [length, width, 0],
        [length, width, 0], [0, width, 0],
        [0, width, 0], [0, 0, 0]
    ]
    
    top_rect = [
        [0, 0, height], [length, 0, height],
        [length, 0, height], [length, width, height],
        [length, width, height], [0, width, height],
        [0, width, height], [0, 0, height]
    ]
    
    vertical = [
        [0, 0, 0], [0, 0, height],
        [length, 0, 0], [length, 0, height],
        [length, width, 0], [length, width, height],
        [0, width, 0], [0, width, height]
    ]
    
    all_edges = bottom_rect + top_rect + vertical
    
    for i in range(0, len(all_edges), 2):
        edges_x.extend([all_edges[i][0], all_edges[i+1][0], None])
        edges_y.extend([all_edges[i][1], all_edges[i+1][1], None])
        edges_z.extend([all_edges[i][2], all_edges[i+1][2], None])
    
    return go.Scatter3d(
        x=edges_x, y=edges_y, z=edges_z,
        mode='lines',
        line=dict(color='gray', width=3),
        name='Truck Trailer',
        hoverinfo='skip',
        showlegend=True
    )


def create_truck_floor_custom(length, width):
    """Create floor with custom dimensions"""
    return go.Mesh3d(
        x=[0, length, length, 0],
        y=[0, 0, width, width],
        z=[0, 0, 0, 0],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color='lightgray',
        opacity=0.2,
        name='Floor',
        hoverinfo='skip',
        showlegend=False
    )