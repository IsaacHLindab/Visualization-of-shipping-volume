"""Geometry utility functions"""

def rotate_dimensions(width, height, rotation):
    """
    Rotate width and height based on rotation angle
    
    Args:
        width: Original width
        height: Original height
        rotation: Rotation angle in degrees (0, 90, 180, 270)
    
    Returns:
        tuple: (adjusted_width, adjusted_height)
    """
    if rotation in [90, 270]:
        return height, width
    return width, height


def calculate_totals(packages):
    """
    Calculate total volume of all packages
    
    Args:
        packages: List of package dictionaries
    
    Returns:
        tuple: (total_volume)
    """
    total_volume = sum(pkg['width'] * pkg['height'] * pkg['depth'] for pkg in packages)
    return total_volume