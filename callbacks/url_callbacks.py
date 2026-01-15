"""Callbacks for handling URL parameters and loading order data"""

from dash import Input, Output, State, html, callback_context
from urllib.parse import urlparse, parse_qs, unquote
import numpy as np

def parse_powerbi_packages(package_string):
    """
    Parse package data from Power BI URL parameter
    Format: Name~Width~Length~Height~Stackable|Name~...
    """
    if not package_string:
        return []
    
    packages = []
    package_type_colors = {
        'EMBV1': 'rgb(59, 130, 246)',   # Blue
        'EMBV2': 'rgb(234, 88, 12)',    # Orange
    }
    
    default_color = 'rgb(156, 163, 175)'

    package_parts = package_string.split('|')
    
    for i, pkg_str in enumerate(package_parts):
        # Skip empty strings (from double separators)
        if not pkg_str or not pkg_str.strip():
            continue
            
        try:
            parts = pkg_str.split('~')
            
            if len(parts) != 5:
                print(f"⚠️ Invalid package format (expected 5, got {len(parts)}): {pkg_str}")
                continue
            
            name, width, length, height, stackable = parts
            package_type = name.split()[0] if name else "Unknown"
            color = package_type_colors.get(package_type, default_color)
            # Convert comma to dot for European decimal format
            width = width.replace(',', '.')
            length = length.replace(',', '.')
            height = height.replace(',', '.')

            package = {
                'id': len(packages) + 1,
                'name': name.strip(),
                'x': 0.0,
                'y': 0.0,
                'z': 0.0,
                'width': float(width),  # Width -> width (X)
                'depth': float(length),  # Length -> depth (Y)
                'height': float(height),  # Height -> height (Z)
                'rotation': 0,
                'color': color,
                'stackable': stackable.strip() in ['1', 'True', 'true', 'TRUE']
            }
            
            packages.append(package)
            
        except ValueError as e:
            print(f"❌ Error parsing package: {pkg_str} - {e}")
            continue
    
    print(f"✅ Loaded {len(packages)} packages from Power BI")
    return packages

def register_callbacks(app):
    """Register URL parameter handling callbacks"""
    
    @app.callback(
        Output('url-order-info', 'children'),
        [Input('url', 'href')]
    )
    def inital_display_order_info(href):
        """Initial dispaly order info"""
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        order_number = params.get('order', [None])[0]
        
        if order_number:
            return html.Div([
                html.Span(f'{order_number}', style={'color': '#3b82f6', 'fontWeight': 'bold'}),
                html.Span(
                    f'', 
                    style={'color': '#94a3b8', 'fontSize': '12px', 'marginLeft': '5px'}
                )
            ])
        
        return html.Div([
            html.Span('No order selected', style={'color': '#94a3b8'})
        ])
    
    @app.callback(
        [Output('packages-store', 'data', allow_duplicate=True),
        Output('package-counter', 'data', allow_duplicate=True)],
        [Input('url', 'href')],
        prevent_initial_call=True
    )
    def load_packages_from_order_data(href):
        """Load packages from order data based on URL parameter from Power BI"""   
        if not href:
            from config import INITIAL_PACKAGES
            return INITIAL_PACKAGES, len(INITIAL_PACKAGES)
        
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        order_number = params.get('order', [None])[0]
        package_data = params.get('packages', [None])[0]
        
        print(f"\n{'='*60}")
        print(f"🔍 POWER BI DATA RECEIVED")
        print(f"{'='*60}")
        print(f"Order ID: {order_number}")
        print(f"Package Data Length: {len(package_data) if package_data else 0} chars")
        if package_data:
            print(f"Package Data Preview: {package_data[:100]}...")
        print(f"{'='*60}\n")
        
        # Try to parse Power BI package data first
        if package_data:
            packages = parse_powerbi_packages(unquote(package_data))
            
            if packages:
                print(f"✅ Parsed {len(packages)} packages from Power BI:")
                for pkg in packages:
                    print(f"   📦 {pkg['name']}: {pkg['width']}x{pkg['depth']}x{pkg['height']}m")
                print()
                return packages, len(packages)
        
        # Fallback to demo packages if only order number provided
        if order_number:
            print(f"⚠️ No package data in URL, using demo packages for order {order_number}")
            packages = create_demo_packages_for_order(order_number)
            return packages, len(packages)
        
        # No order in URL
        from config import INITIAL_PACKAGES
        return INITIAL_PACKAGES, len(INITIAL_PACKAGES)


def create_demo_packages_for_order(order_number):
    """
    Create demo packages based on order number (for POC testing)
    """
    # Create 2-5 packages based on order number (for demo variety)
    try:
        num_packages = (int(order_number) % 4) + 2  # 2-5 packages
    except:
        num_packages = 3
    
    packages = []
    colors = [
        'rgb(59, 130, 246)',   # Blue
        'rgb(234, 88, 12)',    # Orange
        'rgb(34, 197, 94)',    # Green
        'rgb(168, 85, 247)',   # Purple
        'rgb(236, 72, 153)'    # Pink
    ]
    
    for i in range(num_packages):
        packages.append({
            'id': i + 1,
            'name': f'PKG-{order_number}-{i + 1}',
            'x': i * 3.5,  # Space them out along X axis
            'y': 0.0,
            'z': 0.0,
            'width': np.random.uniform(2.5, 3.5),
            'height': np.random.uniform(0.8, 1.2),
            'depth': np.random.uniform(0.8, 1.2),
            'color': colors[i % len(colors)],
            'rotation': 0
        })
    
    return packages