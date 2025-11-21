"""Callbacks for package manipulation (add, delete, rotate, move)"""

from dash import Input, Output, State, callback_context
import dash
import numpy as np
import json
from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT, MOVE_STEP
from utils.geometry import rotate_dimensions


def register_callbacks(app):
    """Register package manipulation callbacks"""
    
    @app.callback(
        [Output('packages-store', 'data'),
         Output('package-counter', 'data')],
        [Input('add-package-btn', 'n_clicks')],
        [State('packages-store', 'data'),
         State('package-counter', 'data')]
    )
    def add_package(n_clicks, packages, counter):
        """Add a new package with random dimensions and position"""
        if n_clicks == 0:
            return packages, counter
        
        ctx = callback_context
        if not ctx.triggered:
            return packages, counter
        
        new_package = {
            'id': counter + 1,
            'name': f'SROR {counter + 1}',
            'x': 0,
            'y': 0,
            'z': 0.0,
            'width': 3,
            'height': 1.2,
            'depth': 0.86,
            'color': f'rgb({np.random.randint(100, 255)}, {np.random.randint(100, 255)}, {np.random.randint(100, 255)})',
            'weight': 300,
            'rotation': 0
        }
        
        packages.append(new_package)
        return packages, counter + 1

    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input({'type': 'delete-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
        [State({'type': 'delete-btn', 'index': dash.dependencies.ALL}, 'id'),
         State('packages-store', 'data')],
        prevent_initial_call=True
    )
    def delete_package(n_clicks, ids, packages):
        """Delete a package"""
        ctx = callback_context
        if not ctx.triggered or not any(n_clicks):
            return packages
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id:
            clicked_id = json.loads(button_id)
            packages = [pkg for pkg in packages if pkg['id'] != clicked_id['index']]
        
        return packages

    @app.callback(
        Output('selected-package-id', 'data'),
        [Input({'type': 'package-item', 'index': dash.dependencies.ALL}, 'n_clicks')],
        [State({'type': 'package-item', 'index': dash.dependencies.ALL}, 'id')]
    )
    def select_package(n_clicks, ids):
        """Handle package selection"""
        ctx = callback_context
        if not ctx.triggered or not any(n_clicks):
            return dash.no_update
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id:
            clicked_id = json.loads(button_id)
            return clicked_id['index']
        
        return dash.no_update

    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('rotate-btn', 'n_clicks')],
        [State('selected-package-id', 'data'),
         State('packages-store', 'data')],
        prevent_initial_call=True
    )
    def rotate_package(n_clicks, selected_id, packages):
        """Rotate the selected package by 90 degrees"""
        if not n_clicks or not packages:
            return packages
        
        for pkg in packages:
            if pkg['id'] == selected_id:
                current_rotation = pkg.get('rotation', 0)
                pkg['rotation'] = (current_rotation + 90) % 360
                
                # Adjust position if package goes out of bounds after rotation
                actual_width, actual_height = rotate_dimensions(
                    pkg['width'], pkg['height'], pkg['rotation']
                )
                pkg['x'] = min(pkg['x'], TRUCK_LENGTH - actual_width)
                pkg['y'] = min(pkg['y'], TRUCK_WIDTH - actual_height)
                break
        
        return packages

    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('align-left-btn', 'n_clicks'),
         Input('align-right-btn', 'n_clicks'),
         Input('align-front-btn', 'n_clicks'),
         Input('align-back-btn', 'n_clicks'),
         Input('align-floor-btn', 'n_clicks')],
        [State('selected-package-id', 'data'),
         State('packages-store', 'data')],
        prevent_initial_call=True
    )
    def align_package(left_clicks, right_clicks, front_clicks, back_clicks, 
                     floor_clicks, selected_id, packages):
        """Align package to truck walls"""
        ctx = callback_context
        if not ctx.triggered or not packages:
            return packages
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        for pkg in packages:
            if pkg['id'] == selected_id:
                rotation = pkg.get('rotation', 0)
                actual_width, actual_height = rotate_dimensions(
                    pkg['width'], pkg['height'], rotation
                )
                
                if button_id == 'align-left-btn':
                    pkg['y'] = 0
                elif button_id == 'align-right-btn':
                    pkg['y'] = TRUCK_WIDTH - actual_height
                elif button_id == 'align-front-btn':
                    pkg['x'] = 0
                elif button_id == 'align-back-btn':
                    pkg['x'] = TRUCK_LENGTH - actual_width
                elif button_id == 'align-floor-btn':
                    pkg['z'] = 0
                break
        
        return packages

    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('x-minus-btn', 'n_clicks'),
         Input('x-plus-btn', 'n_clicks'),
         Input('y-minus-btn', 'n_clicks'),
         Input('y-plus-btn', 'n_clicks'),
         Input('z-minus-btn', 'n_clicks'),
         Input('z-plus-btn', 'n_clicks')],
        [State('selected-package-id', 'data'),
         State('packages-store', 'data')],
        prevent_initial_call=True
    )
    def move_package_buttons(x_minus, x_plus, y_minus, y_plus, z_minus, z_plus, 
                            selected_id, packages):
        """Move package using +/- buttons"""
        ctx = callback_context
        if not ctx.triggered or not packages:
            return packages
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        for pkg in packages:
            if pkg['id'] == selected_id:
                rotation = pkg.get('rotation', 0)
                actual_width, actual_height = rotate_dimensions(
                    pkg['width'], pkg['height'], rotation
                )
                
                if button_id == 'x-minus-btn':
                    pkg['x'] = max(0, pkg['x'] - MOVE_STEP)
                elif button_id == 'x-plus-btn':
                    pkg['x'] = min(TRUCK_LENGTH - actual_width, pkg['x'] + MOVE_STEP)
                elif button_id == 'y-minus-btn':
                    pkg['y'] = max(0, pkg['y'] - MOVE_STEP)
                elif button_id == 'y-plus-btn':
                    pkg['y'] = min(TRUCK_WIDTH - actual_height, pkg['y'] + MOVE_STEP)
                elif button_id == 'z-minus-btn':
                    pkg['z'] = max(0, pkg['z'] - MOVE_STEP)
                elif button_id == 'z-plus-btn':
                    pkg['z'] = min(TRUCK_HEIGHT - pkg['depth'], pkg['z'] + MOVE_STEP)
                break
        
        return packages

    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('input-x', 'value'),
         Input('input-y', 'value'),
         Input('input-z', 'value')],
        [State('selected-package-id', 'data'),
         State('packages-store', 'data')],
        prevent_initial_call=True
    )
    def update_package_position(x, y, z, selected_id, packages):
        """Update the position of the selected package from numeric inputs"""
        if not packages or x is None or y is None or z is None:
            return packages
        
        for pkg in packages:
            if pkg['id'] == selected_id:
                rotation = pkg.get('rotation', 0)
                actual_width, actual_height = rotate_dimensions(
                    pkg['width'], pkg['height'], rotation
                )
                
                pkg['x'] = max(0, min(TRUCK_LENGTH - actual_width, x))
                pkg['y'] = max(0, min(TRUCK_WIDTH - actual_height, y))
                pkg['z'] = max(0, min(TRUCK_HEIGHT - pkg['depth'], z))
                break
        
        return packages