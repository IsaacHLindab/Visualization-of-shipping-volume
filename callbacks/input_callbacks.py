"""Callbacks for keyboard and input handling"""

from dash import Input, Output, State
from config import TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT, MOVE_STEP
from utils.geometry import rotate_dimensions


def register_callbacks(app):
    """Register input handling callbacks"""
    
    @app.callback(
        Output('packages-store', 'data', allow_duplicate=True),
        [Input('keyboard-listener', 'n_events')],
        [State('keyboard-listener', 'event'),
         State('selected-package-id', 'data'),
         State('packages-store', 'data')],
        prevent_initial_call=True
    )
    def handle_keyboard(n_events, event, selected_id, packages):
        """Handle keyboard shortcuts for package movement"""
        if not event or not packages or selected_id is None:
            return packages
        
        key = event.get('key', '').lower()
        
        for pkg in packages:
            if pkg['id'] == selected_id:
                rotation = pkg.get('rotation', 0)
                actual_width, actual_height = rotate_dimensions(
                    pkg['width'], pkg['height'], rotation
                )
                
                # Arrow keys for XY movement
                if key == 'arrowleft':
                    pkg['y'] = max(0, pkg['y'] - MOVE_STEP)
                elif key == 'arrowright':
                    pkg['y'] = min(TRUCK_WIDTH - actual_height, pkg['y'] + MOVE_STEP)
                elif key == 'arrowup':
                    pkg['x'] = max(0, pkg['x'] - MOVE_STEP)
                elif key == 'arrowdown':
                    pkg['x'] = min(TRUCK_LENGTH - actual_width, pkg['x'] + MOVE_STEP)
                
                # PageUp/PageDown for Z movement
                elif key == 'pageup':
                    pkg['z'] = min(TRUCK_HEIGHT - pkg['depth'], pkg['z'] + MOVE_STEP)
                elif key == 'pagedown':
                    pkg['z'] = max(0, pkg['z'] - MOVE_STEP)
                
                # R for rotation
                elif key == 'r':
                    current_rotation = pkg.get('rotation', 0)
                    pkg['rotation'] = (current_rotation + 90) % 360
                    
                    # Adjust position if out of bounds after rotation
                    new_width, new_height = rotate_dimensions(
                        pkg['width'], pkg['height'], pkg['rotation']
                    )
                    pkg['x'] = min(pkg['x'], TRUCK_LENGTH - new_width)
                    pkg['y'] = min(pkg['y'], TRUCK_WIDTH - new_height)
                
                break
        
        return packages