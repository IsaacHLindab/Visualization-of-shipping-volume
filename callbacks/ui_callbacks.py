"""Callbacks for UI updates (summary stats, package list, controls)"""

from dash import Input, Output, State, html, dcc
from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT, MOVE_STEP, DEFAULT_CAMERA
from utils.geometry import rotate_dimensions, calculate_totals
from visualization.figures import create_figure


def register_callbacks(app):
    """Register UI update callbacks"""
    
    @app.callback(
        Output('summary-stats', 'children'),
        [Input('packages-store', 'data')]
    )
    def update_summary(packages):
        """Update summary statistics"""
        if not packages:
            return html.Div('No packages loaded', style={'color': '#94a3b8'})
        
        total_weight, total_volume = calculate_totals(packages)
        truck_volume = TRUCK_LENGTH * TRUCK_WIDTH * TRUCK_HEIGHT
        utilization = (total_volume / truck_volume) * 100
        
        return html.Div([
            html.Div(f'📦 Total Packages: {len(packages)}', style={'marginBottom': '5px'}),
            html.Div(f'⚖️ Total Weight: {total_weight:.1f} kg', style={'marginBottom': '5px'}),
            html.Div(f'📐 Total Volume: {total_volume:.2f} m³', style={'marginBottom': '5px'}),
            html.Div(f'📊 Utilization: {utilization:.1f}%', style={'marginBottom': '5px'})
        ])

    @app.callback(
        Output('package-list', 'children'),
        [Input('packages-store', 'data'),
         Input('selected-package-id', 'data')]
    )
    def update_package_list(packages, selected_id):
        """Update the list of packages in the sidebar"""
        if not packages:
            return html.Div('No packages', style={'color': '#94a3b8'})
        
        package_items = []
        for pkg in packages:
            is_selected = pkg['id'] == selected_id
            rotation = pkg.get('rotation', 0)
            actual_width, actual_height = rotate_dimensions(
                pkg['width'], pkg['height'], rotation
            )
            
            package_items.append(
                html.Div([
                    html.Div([
                        html.Span(pkg['name'], style={'fontWeight': 'bold'}),
                        html.Button(
                            '🗑️',
                            id={'type': 'delete-btn', 'index': pkg['id']},
                            n_clicks=0,
                            style={
                                'float': 'right',
                                'background': 'none',
                                'border': 'none',
                                'color': '#ef4444',
                                'cursor': 'pointer',
                                'fontSize': '16px'
                            }
                        )
                    ]),
                    html.Div([
                        html.Div(
                            style={
                                'width': '20px',
                                'height': '20px',
                                'backgroundColor': pkg['color'],
                                'display': 'inline-block',
                                'marginRight': '10px',
                                'borderRadius': '3px'
                            }
                        ),
                        html.Span(
                            f"Size: {actual_width:.1f} × {actual_height:.1f} × {pkg['depth']:.1f}m",
                            style={'fontSize': '12px', 'color': '#cbd5e1'}
                        )
                    ], style={'marginTop': '5px'}),
                    html.Div([
                        html.Span(
                            f"Pos: ({pkg['x']:.2f}, {pkg['y']:.2f}, {pkg['z']:.2f}) | ",
                            style={'fontSize': '12px', 'color': '#cbd5e1'}
                        ),
                        html.Span(
                            f"Rot: {rotation}° | ",
                            style={'fontSize': '12px', 'color': '#cbd5e1'}
                        ),
                        html.Span(
                            f"{pkg['weight']:.0f}kg",
                            style={'fontSize': '12px', 'color': '#cbd5e1'}
                        )
                    ], style={'marginTop': '3px'})
                ], id={'type': 'package-item', 'index': pkg['id']},
                n_clicks=0,
                style={
                    'padding': '10px',
                    'marginBottom': '10px',
                    'backgroundColor': '#3b82f6' if is_selected else '#334155',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'border': '2px solid #3b82f6' if is_selected else '2px solid transparent'
                })
            )
        
        return package_items

    @app.callback(
    Output('package-controls', 'children'),
    [Input('selected-package-id', 'data'),
     Input('packages-store', 'data')]
    )
    def update_controls(selected_id, packages):
        """Update the control interface for the selected package"""
        if not packages:
            return html.Div('No packages loaded', style={'color': '#94a3b8', 'textAlign': 'center'})
        
        selected_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        
        if not selected_pkg:
            return html.Div('Select a package to edit', style={'color': '#94a3b8', 'textAlign': 'center'})
        
        from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT
        
        return html.Div([
            html.H4(f'Editing: {selected_pkg["name"]}', 
                    style={'color': '#3b82f6', 'marginBottom': '15px'}),
            
            # Rotation control
            html.Div([
                html.Label('Rotation:', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Button('🔄 Rotate 90°', id='rotate-btn', n_clicks=0,
                        style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'})
            ]),
            
            # Position controls with SLIDERS
            html.Div([
                html.Label('Position:', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                
                # X Position
                html.Div([
                    html.Div([
                        html.Span('X (Length): ', style={'color': '#94a3b8', 'fontSize': '12px'}),
                        html.Span(f'{selected_pkg["x"]:.2f}m', 
                                id='x-display',
                                style={'color': '#3b82f6', 'fontWeight': 'bold', 'fontSize': '14px'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='slider-x',
                        min=0,
                        max=TRUCK_LENGTH - selected_pkg['width'],
                        step=0.1,
                        value=selected_pkg['x'],
                        marks={0: '0m', TRUCK_LENGTH: f'{TRUCK_LENGTH}m'},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], style={'marginBottom': '15px'}),
                
                # Y Position
                html.Div([
                    html.Div([
                        html.Span('Y (Width): ', style={'color': '#94a3b8', 'fontSize': '12px'}),
                        html.Span(f'{selected_pkg["y"]:.2f}m', 
                                id='y-display',
                                style={'color': '#3b82f6', 'fontWeight': 'bold', 'fontSize': '14px'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='slider-y',
                        min=0,
                        max=TRUCK_WIDTH - selected_pkg['depth'],
                        step=0.1,
                        value=selected_pkg['y'],
                        marks={0: '0m', TRUCK_WIDTH: f'{TRUCK_WIDTH}m'},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], style={'marginBottom': '15px'}),
                
                # Z Position
                html.Div([
                    html.Div([
                        html.Span('Z (Height): ', style={'color': '#94a3b8', 'fontSize': '12px'}),
                        html.Span(f'{selected_pkg["z"]:.2f}m', 
                                id='z-display',
                                style={'color': '#3b82f6', 'fontWeight': 'bold', 'fontSize': '14px'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='slider-z',
                        min=0,
                        max=TRUCK_HEIGHT - selected_pkg['height'],
                        step=0.1,
                        value=selected_pkg['z'],
                        marks={0: '0m', TRUCK_HEIGHT: f'{TRUCK_HEIGHT}m'},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], style={'marginBottom': '15px'}),
                
            ], style={
                'padding': '15px',
                'backgroundColor': '#334155',
                'borderRadius': '5px',
                'marginBottom': '15px'
            }),
            
            # Quick alignment buttons
            html.Div([
                html.Label('Quick Align:', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Div([
                    html.Button('⬅️ Left', id='align-left-btn', n_clicks=0,
                            style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                    html.Button('➡️ Right', id='align-right-btn', n_clicks=0,
                            style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                ], style={'display': 'flex', 'marginBottom': '5px'}),
                html.Div([
                    html.Button('⬇️ Front', id='align-front-btn', n_clicks=0,
                            style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                    html.Button('⬆️ Back', id='align-back-btn', n_clicks=0,
                            style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                ], style={'display': 'flex', 'marginBottom': '5px'}),
                html.Button('⬇️ Floor', id='align-floor-btn', n_clicks=0,
                        style={'width': '100%', 'padding': '5px', 'fontSize': '11px'})
            ], style={'marginBottom': '15px'}),
            
            # Delete button
            html.Button('🗑️ Delete Package', 
                    id='delete-package-btn',
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': '#dc2626',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold'
                    })
        ])

    @app.callback(
        Output('truck-3d-graph', 'figure'),
        [Input('packages-store', 'data')]
    )
    def update_graph(packages):
        """Update the 3D visualization"""
        return create_figure(packages, DEFAULT_CAMERA)

    @app.callback(
        Output('camera-store', 'data'),
        [Input('truck-3d-graph', 'relayoutData')],
        [State('camera-store', 'data')]
    )
    def store_camera(relayout_data, current_camera):
        """Store camera position when user moves it"""
        if relayout_data and 'scene.camera' in relayout_data:
            return relayout_data['scene.camera']
        return current_camera
    
    @app.callback(
    Output('camera-display', 'children'),
    [Input('truck-3d-graph', 'relayoutData')]
    )
    def display_camera_position(relayout_data):
        """Display current camera position for easy config copying"""
        if relayout_data and 'scene.camera' in relayout_data:
            camera = relayout_data['scene.camera']
            eye = camera.get('eye', {})
            center = camera.get('center', {})
            up = camera.get('up', {})
            
            return html.Pre(f"""DEFAULT_CAMERA = {{
        'eye': {{'x': {eye.get('x', 0):.2f}, 'y': {eye.get('y', 0):.2f}, 'z': {eye.get('z', 0):.2f}}},
        'center': {{'x': {center.get('x', 0):.2f}, 'y': {center.get('y', 0):.2f}, 'z': {center.get('z', 0):.2f}}},
        'up': {{'x': {up.get('x', 0):.2f}, 'y': {up.get('y', 0):.2f}, 'z': {up.get('z', 0):.2f}}}
    }}""", style={'margin': '0', 'whiteSpace': 'pre-wrap'})
        
        return "Rotate the 3D view to see camera values..."


def _create_quick_actions():
    """Create quick action buttons section"""
    return html.Div([
        html.Label('Quick Actions', style={'fontSize': '14px', 'marginBottom': '10px', 'display': 'block'}),
        html.Div([
            html.Button(
                '🔄 Rotate 90°', id='rotate-btn', n_clicks=0,
                style=_button_style('#8b5cf6', '5px')
            ),
            html.Button(
                '⬅️ To Left', id='align-left-btn', n_clicks=0,
                style=_button_style('#10b981', '5px')
            ),
            html.Button(
                '➡️ To Right', id='align-right-btn', n_clicks=0,
                style=_button_style('#10b981', '5px')
            ),
        ], style={'marginBottom': '10px'}),
        html.Div([
            html.Button(
                '⬆️ To Front', id='align-front-btn', n_clicks=0,
                style=_button_style('#10b981', '5px')
            ),
            html.Button(
                '⬇️ To Back', id='align-back-btn', n_clicks=0,
                style=_button_style('#10b981', '5px')
            ),
            html.Button(
                '⬇️ To Floor', id='align-floor-btn', n_clicks=0,
                style=_button_style('#10b981', '0px')
            ),
        ])
    ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#334155', 'borderRadius': '5px'})


def _create_position_control(axis, label, value, max_value):
    """Create a position control with +/- buttons and input"""
    return html.Div([
        html.Label(f'Position {axis} ({label})', style={'fontSize': '14px', 'marginBottom': '5px'}),
        html.Div([
            html.Button('−', id=f'{axis.lower()}-minus-btn', n_clicks=0, 
                       style={'padding': '5px 15px', 'fontSize': '16px', 'cursor': 'pointer'}),
            dcc.Input(
                id=f'input-{axis.lower()}',
                type='number',
                value=round(value, 2),
                step=MOVE_STEP,
                min=0,
                max=max_value,
                style={
                    'width': '100px',
                    'margin': '0 10px',
                    'padding': '5px',
                    'textAlign': 'center'
                }
            ),
            html.Button('+', id=f'{axis.lower()}-plus-btn', n_clicks=0,
                       style={'padding': '5px 15px', 'fontSize': '16px', 'cursor': 'pointer'}),
            html.Span(f' m (max: {max_value:.2f})', 
                     style={'marginLeft': '10px', 'fontSize': '12px', 'color': '#94a3b8'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '5px'})
    ], style={'marginBottom': '20px'})


def _button_style(bg_color, margin_right):
    """Helper to create consistent button styles"""
    return {
        'padding': '8px 12px',
        'backgroundColor': bg_color,
        'color': 'white',
        'border': 'none',
        'borderRadius': '5px',
        'cursor': 'pointer',
        'marginRight': margin_right,
        'fontSize': '12px'
    }
