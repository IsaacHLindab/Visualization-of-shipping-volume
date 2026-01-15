"""Callbacks for UI updates (summary stats, package list, controls)"""

from dash import Input, Output, State, html, dcc
import dash
from dash.exceptions import PreventUpdate
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
        
        total_volume = calculate_totals(packages)
        truck_volume = TRUCK_LENGTH * TRUCK_WIDTH * TRUCK_HEIGHT
        utilization = (total_volume / truck_volume) * 100
        
        return html.Div([
            html.Div(f'📦 Total Packages: {len(packages)}', style={'marginBottom': '5px'}),
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
        Output('truck-3d-graph', 'figure'),
        [Input('packages-store', 'data'),
        Input('truck-dimensions', 'data')]
    )
    def update_graph(packages, truck_dims):
        """Update the 3D visualization"""
        if truck_dims:
            from visualization.figures import create_figure_custom
            return create_figure_custom(packages, DEFAULT_CAMERA, truck_dims)
        else:
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
    [Output('selected-package-name', 'children'),
     Output('slider-x', 'disabled'),
     Output('slider-y', 'disabled'),
     Output('slider-z', 'disabled'),
     Output('slider-x', 'max'),
     Output('slider-y', 'max'),
     Output('slider-z', 'max'),
     Output('input-width', 'disabled'),
     Output('input-depth', 'disabled'),
     Output('input-height', 'disabled'),
     Output('stackable-container', 'style')],
    [Input('selected-package-id', 'data'),
     Input('packages-store', 'data')]
    )
    def update_slider_state(selected_id, packages):
        """Enable/disable sliders and set max values based on selected package"""
        if not packages or not selected_id:
            return (
                'Select a package to edit',
                True, True, True,  # Sliders disabled
                TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT,
                True, True, True, # Inputs disabled
                {'display': 'none'} # stackable check box hidden
            )
        
        selected_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        if not selected_pkg:
            return (
                'Select a package to edit',
                True, True, True,
                TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT,
                True, True, True,
                {'display': 'none'}
            )
        
        # Calculate max values based on package dimensions
        rotation = selected_pkg.get('rotation', 0)
        actual_width, actual_height = rotate_dimensions(
            selected_pkg['width'], selected_pkg['height'], rotation
        )
        
        max_x = TRUCK_LENGTH - actual_width
        max_y = TRUCK_WIDTH - actual_height
        max_z = TRUCK_HEIGHT - selected_pkg['depth']
        
        return (
            f"Editing: {selected_pkg['name']}",
            False, False, False,  # Sliders enabled
            max_x, max_y, max_z,
            False, False, False,  # Inputs enabled
            {'display': 'block', 'fontSize': '12px', 'marginBottom': '10px'}  # Visible stackable checkbox
        )


    @app.callback(
        [Output('slider-x', 'value'),
        Output('slider-y', 'value'),
        Output('slider-z', 'value'),
        Output('x-position-display', 'children'),
        Output('y-position-display', 'children'),
        Output('z-position-display', 'children')],
        [Input('selected-package-id', 'data'),
        Input('packages-store', 'data')]
    )
    def update_slider_values(selected_id, packages):
        """Update slider values to match selected package position"""
        if not packages or not selected_id:
            return 0, 0, 0, 'X: --', 'Y: --', 'Z: --'
        
        selected_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        if not selected_pkg:
            return 0, 0, 0, 'X: --', 'Y: --', 'Z: --'
        
        x = selected_pkg['x']
        y = selected_pkg['y']
        z = selected_pkg['z']
        
        return (
            x, y, z,
            f'X (Length): {x:.2f}m',
            f'Y (Width): {y:.2f}m',
            f'Z (Height): {z:.2f}m'
    )
    
    @app.callback(
        [Output('input-width', 'value'),
        Output('input-depth', 'value'),
        Output('input-height', 'value')],
        [Input('selected-package-id', 'data'),
        Input('packages-store', 'data')]
    )
    def update_property_inputs(selected_id, packages):
        """Update property input values to match selected package"""
        if not packages or not selected_id:
            return None, None, None
        
        selected_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        if not selected_pkg:
            return None, None, None
        
        return (
            selected_pkg['width'],
            selected_pkg['depth'],
            selected_pkg['height']
        )
    
    @app.callback(
    Output('truck-dimensions', 'data'),
    [Input('input-truck-length', 'value'),
     Input('input-truck-width', 'value'),
     Input('input-truck-height', 'value'),
     Input('reset-truck-btn', 'n_clicks')],
    [State('truck-dimensions', 'data')],
    prevent_initial_call=True
    )
    def update_truck_dimensions(length, width, height, reset_clicks, current_dims):
        """Update truck dimensions or reset to default"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset to default
        if trigger_id == 'reset-truck-btn':
            from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT
            print(f"🔄 Reset truck to default: {TRUCK_LENGTH}x{TRUCK_WIDTH}x{TRUCK_HEIGHT}m")
            return {
                'length': TRUCK_LENGTH,
                'width': TRUCK_WIDTH,
                'height': TRUCK_HEIGHT
            }
        
        # Update individual dimension
        new_dims = {**current_dims}
        
        if trigger_id == 'input-truck-length' and length and length >= 1:
            if abs(new_dims['length'] - length) > 0.01:  # Only if changed
                new_dims['length'] = length
                print(f"📏 Updated truck length: {length}m")
        elif trigger_id == 'input-truck-width' and width and width >= 1:
            if abs(new_dims['width'] - width) > 0.01:
                new_dims['width'] = width
                print(f"📏 Updated truck width: {width}m")
        elif trigger_id == 'input-truck-height' and height and height >= 1:
            if abs(new_dims['height'] - height) > 0.01:
                new_dims['height'] = height
                print(f"📏 Updated truck height: {height}m")
        else:
            raise PreventUpdate
        
        return new_dims
    
    @app.callback(
    [Output('input-truck-length', 'value'),
     Output('input-truck-width', 'value'),
     Output('input-truck-height', 'value')],
    [Input('reset-truck-btn', 'n_clicks')],
    prevent_initial_call=True
    )
    def reset_truck_inputs(n_clicks):
        """Reset truck dimension inputs to default"""
        from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT
        return TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT

    @app.callback(
    Output('input-stackable', 'value'),
    [Input('selected-package-id', 'data'),
     Input('packages-store', 'data')]
    )
    def update_stackable_checkbox(selected_id, packages):
        """Update stackable checkbox to match selected package"""
        if not packages or not selected_id:
            return []
        
        selected_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        if not selected_pkg:
            return []
        
        return ['stackable'] if selected_pkg.get('stackable', False) else []

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