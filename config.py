"""Configuration constants for the truck loading application"""

TRUCK_LENGTH = 13.6
TRUCK_WIDTH = 2.45
TRUCK_HEIGHT = 2.7

MOVE_STEP = 0.25  # 25cm increments

INITIAL_PACKAGES = [
    {
        'id': 1,
        'name': 'SROR 1',
        'x': 0.0, 'y': 0.0, 'z': 0.0,
        'width': 3.0, 'height': 0.86, 'depth': 1.2,
        'color': 'rgb(59, 130, 246)',
        'rotation': 0  # 0, 90, 180, 270 degrees
    }
]

DEFAULT_CAMERA = {
        'eye': {'x': 4.46, 'y': 4.51, 'z': 1.87},
        'center': {'x': 0.00, 'y': 0.00, 'z': 0.00},
        'up': {'x': 0.00, 'y': 0.00, 'z': 1.00}
}