"""Callbacks for package manipulation (add, delete, rotate, move)"""

from dash import Input, Output, State, callback_context, ALL
import dash
from dash.exceptions import PreventUpdate
import numpy as np
import json
from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT, MOVE_STEP
from utils.geometry import rotate_dimensions

def calculate_stack_position(selected_pkg, all_packages, truck_height):
    """
    Calculate the Z position for a package based on overlapping packages.
    Returns None if no stacking needed, or the new Z position if stacking.
    """
    
    rotation = selected_pkg.get('rotation', 0)
    actual_width, actual_height = rotate_dimensions(
        selected_pkg['width'], selected_pkg['height'], rotation
    )
    
    sel_x1 = selected_pkg['x']
    sel_x2 = selected_pkg['x'] + actual_width
    sel_y1 = selected_pkg['y']
    sel_y2 = selected_pkg['y'] + actual_height
    
    max_z = 0
    found_overlap = False
    
    for other_pkg in all_packages:
        if other_pkg['id'] == selected_pkg['id']:
            continue
        
        other_rotation = other_pkg.get('rotation', 0)
        other_width, other_height = rotate_dimensions(
            other_pkg['width'], other_pkg['height'], other_rotation
        )
        
        other_x1 = other_pkg['x']
        other_x2 = other_pkg['x'] + other_width
        other_y1 = other_pkg['y']
        other_y2 = other_pkg['y'] + other_height
        
        # Check overlap
        x_overlap = not (sel_x2 <= other_x1 or sel_x1 >= other_x2)
        y_overlap = not (sel_y2 <= other_y1 or sel_y1 >= other_y2)
        
        if x_overlap and y_overlap:
            found_overlap = True
            other_top = other_pkg['z'] + other_pkg['depth']
            if other_top > max_z:
                max_z = other_top
    
    if found_overlap and max_z > 0:
        new_z = max_z + 0.1
        
        # Check if it fits in truck
        if new_z + selected_pkg['depth'] <= truck_height:
            return round(new_z, 2)
        else:
            # Would exceed truck height
            return None
    
    # No overlap found
    return 0.0

def update_package_with_stacking(pkg, packages, auto_stack, truck_height, action_type="moved"):
    """
    Update package position with optional auto-stacking logic.
    
    Args:
        pkg: The package dict with updated x/y position
        packages: All packages (for overlap detection)
        auto_stack: Auto-stack toggle value
        truck_height: Maximum truck height
        action_type: String for logging ("moved", "grid placed", "slider moved")
    
    Returns:
        tuple: (updated_pkg, log_message)
    """
    if auto_stack and 'enabled' in auto_stack and pkg.get('stackable', False):
        new_z = calculate_stack_position(pkg, packages, truck_height)
        
        if new_z is not None:
            pkg['z'] = new_z
            if new_z > 0:
                return pkg, f"📍 {action_type.capitalize()} + auto-stacked {pkg['name']} at ({pkg['x']:.1f}, {pkg['y']:.1f}, {new_z:.2f})"
            else:
                return pkg, f"📍 {action_type.capitalize()} {pkg['name']} to ground ({pkg['x']:.1f}, {pkg['y']:.1f})"
        else:
            # Can't stack - exceeds height
            return pkg, f"📍 {action_type.capitalize()} {pkg['name']} to ({pkg['x']:.1f}, {pkg['y']:.1f}, {pkg['z']:.1f}) - can't stack (exceeds height)"
    else:
        # Auto-stack disabled or not stackable
        return pkg, f"📍 {action_type.capitalize()} {pkg['name']} to ({pkg['x']:.1f}, {pkg['y']:.1f}, {pkg['z']:.1f})"


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
        [Input({'type': 'grid-cell', 'x': ALL, 'y': ALL}, 'n_clicks')],
        [State('packages-store', 'data'),
        State('selected-package-id', 'data'),
        State('auto-stack-toggle', 'value'),
        State('truck-dimensions', 'data')],
        prevent_initial_call=True
    )
    def position_package_from_grid(n_clicks_list, packages, selected_id, auto_stack, truck_dims):
        """Move package to clicked grid cell with optional auto-stacking"""
        if not packages or not selected_id:
            raise PreventUpdate
        
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        # Find which cell was clicked
        trigger = ctx.triggered[0]
        if trigger['value'] == 0:  # No actual click
            raise PreventUpdate
        
        # Parse the cell coordinates from the trigger ID
        trigger_id = json.loads(trigger['prop_id'].split('.')[0])
        cell_x = trigger_id['x']
        cell_y = trigger_id['y']

        truck_height = truck_dims.get('height', TRUCK_HEIGHT) if truck_dims else TRUCK_HEIGHT
        
        # Update selected package position
        updated_packages = []
        for pkg in packages:
            if pkg['id'] == selected_id:
                # Update X/Y position
                pkg['x'] = cell_x
                pkg['y'] = cell_y
                
                # Apply stacking logic and get log message
                pkg, log_msg = update_package_with_stacking(pkg, packages, auto_stack, truck_height, "grid placed")
                print(log_msg)
                
            updated_packages.append(pkg)
        
        return updated_packages

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
    
    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('slider-x', 'value'),
        Input('slider-y', 'value'),
        Input('slider-z', 'value')],
        [State('packages-store', 'data'),
        State('selected-package-id', 'data'),
        State('auto-stack-toggle', 'value'),
        State('truck-dimensions', 'data')],
        prevent_initial_call=True
    )
    def update_position_from_sliders(x_val, y_val, z_val, packages, selected_id, auto_stack, truck_dims):
        """Update package position based on slider values, with optional auto-stacking"""
        if not packages or not selected_id:
            raise PreventUpdate
        
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        current_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        if not current_pkg:
            raise PreventUpdate
        
        # Check if value actually changed
        value_changed = False
        if trigger_id == 'slider-x' and x_val is not None and abs(current_pkg['x'] - x_val) > 0.01:
            value_changed = True
        elif trigger_id == 'slider-y' and y_val is not None and abs(current_pkg['y'] - y_val) > 0.01:
            value_changed = True
        elif trigger_id == 'slider-z' and z_val is not None and abs(current_pkg['z'] - z_val) > 0.01:
            value_changed = True
        
        if not value_changed:
            raise PreventUpdate
        
        truck_height = truck_dims.get('height', TRUCK_HEIGHT) if truck_dims else TRUCK_HEIGHT
        
        updated_packages = []
        for pkg in packages:
            if pkg['id'] == selected_id:
                updated_pkg = {**pkg}
                
                # Update position
                if trigger_id == 'slider-x' and x_val is not None:
                    updated_pkg['x'] = round(x_val, 2)
                elif trigger_id == 'slider-y' and y_val is not None:
                    updated_pkg['y'] = round(y_val, 2)
                elif trigger_id == 'slider-z' and z_val is not None:
                    updated_pkg['z'] = round(z_val, 2)
                
                # Apply auto-stacking only for X/Y changes, not Z
                if trigger_id in ['slider-x', 'slider-y']:
                    updated_pkg, log_msg = update_package_with_stacking(updated_pkg, packages, auto_stack, truck_height, "slider moved")
                    print(log_msg)
                else:
                    # Manual Z change - just log it
                    print(f"📍 Moved {updated_pkg['name']} to ({updated_pkg['x']:.1f}, {updated_pkg['y']:.1f}, {updated_pkg['z']:.1f})")
                
                updated_packages.append(updated_pkg)
            else:
                updated_packages.append(pkg)
        
        return updated_packages
    
    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('input-width', 'value'),
        Input('input-depth', 'value'),
        Input('input-height', 'value'),
        Input('input-weight', 'value'),
        Input('input-stackable', 'value')],
        [State('selected-package-id', 'data'),
        State('packages-store', 'data'),
        State('truck-dimensions', 'data')],  # ADD THIS
        prevent_initial_call=True
    )
    def update_package_properties(width, depth, height, weight, stackable, selected_id, packages, truck_dims):
        """Update package dimensions, weight, and stackable property"""
        if not packages or not selected_id:
            raise PreventUpdate
        
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Handle stackable checkbox
        if trigger_id == 'input-stackable':
            updated_packages = []
            for pkg in packages:
                if pkg['id'] == selected_id:
                    updated_pkg = {**pkg}
                    updated_pkg['stackable'] = 'stackable' in (stackable or [])
                    print(f"📦 Updated stackable: {updated_pkg['stackable']}")
                    updated_packages.append(updated_pkg)
                else:
                    updated_packages.append(pkg)
            return updated_packages
        
        # Get current package to check if value actually changed
        current_pkg = next((pkg for pkg in packages if pkg['id'] == selected_id), None)
        if not current_pkg:
            raise PreventUpdate
        
        # Check if value actually changed (prevent spam from position updates)
        value_changed = False
        if trigger_id == 'input-width' and width is not None:
            if abs(current_pkg['width'] - width) > 0.001:
                value_changed = True
        elif trigger_id == 'input-depth' and depth is not None:
            if abs(current_pkg['depth'] - depth) > 0.001:
                value_changed = True
        elif trigger_id == 'input-height' and height is not None:
            if abs(current_pkg['height'] - height) > 0.001:
                value_changed = True
        elif trigger_id == 'input-weight' and weight is not None:
            if abs(current_pkg['weight'] - weight) > 0.1:
                value_changed = True
        
        if not value_changed:
            raise PreventUpdate
        
        # Validate inputs
        if width is not None and width < 0.1:
            raise PreventUpdate
        if depth is not None and depth < 0.5:
            raise PreventUpdate
        if height is not None and height < 0.5:
            raise PreventUpdate
        if weight is not None and weight < 50:
            raise PreventUpdate
        
        # Get truck dimensions (use custom or defaults)
        truck_length = truck_dims.get('length', TRUCK_LENGTH) if truck_dims else TRUCK_LENGTH
        truck_width = truck_dims.get('width', TRUCK_WIDTH) if truck_dims else TRUCK_WIDTH
        truck_height = truck_dims.get('height', TRUCK_HEIGHT) if truck_dims else TRUCK_HEIGHT
        
        updated_packages = []
        for pkg in packages:
            if pkg['id'] == selected_id:
                updated_pkg = {**pkg}
                
                if trigger_id == 'input-width' and width is not None:
                    updated_pkg['width'] = round(width, 2)
                    print(f"📏 Updated width: {width:.2f}m")
                elif trigger_id == 'input-depth' and depth is not None:
                    updated_pkg['depth'] = round(depth, 2)
                    print(f"📏 Updated depth: {depth:.2f}m")
                elif trigger_id == 'input-height' and height is not None:
                    updated_pkg['height'] = round(height, 2)
                    print(f"📏 Updated height: {height:.2f}m")
                elif trigger_id == 'input-weight' and weight is not None:
                    updated_pkg['weight'] = round(weight, 1)
                    print(f"⚖️ Updated weight: {weight:.1f}kg")
                
                # Ensure package doesn't go out of bounds after dimension change
                rotation = updated_pkg.get('rotation', 0)
                actual_width, actual_height = rotate_dimensions(
                    updated_pkg['width'], updated_pkg['height'], rotation
                )
                updated_pkg['x'] = min(updated_pkg['x'], truck_length - actual_width)
                updated_pkg['y'] = min(updated_pkg['y'], truck_width - actual_height)
                updated_pkg['z'] = min(updated_pkg['z'], truck_height - updated_pkg['depth'])
                
                updated_packages.append(updated_pkg)
            else:
                updated_packages.append(pkg)
        
        return updated_packages
