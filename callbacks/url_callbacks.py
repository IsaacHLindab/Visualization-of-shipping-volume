"""Callbacks for handling URL parameters and loading order data"""

from dash import Input, Output, State, html, callback_context
from urllib.parse import urlparse, parse_qs
import numpy as np


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
                html.Span('📋 Order: ', style={'color': '#cbd5e1'}),
                html.Span(order_number, style={'color': '#3b82f6', 'fontWeight': 'bold'}),
                html.Span(
                    f'', 
                    style={'color': '#94a3b8', 'fontSize': '12px', 'marginLeft': '5px'}
                )
            ])
        
        return html.Div([
            html.Span('📋 ', style={'marginRight': '5px'}),
            html.Span('No order selected', style={'color': '#94a3b8'})
        ])
    
    @app.callback(
        [Output('packages-store', 'data', allow_duplicate=True),
         Output('package-counter', 'data', allow_duplicate=True),],
        [Input('url', 'href'),
         Input('load-order-btn', 'n_clicks')],
        [State('order-input', 'value')],
        prevent_initial_call=True
    )
    def load_packages_from_order_data(href, load_clicks, manual_order):
        """Loads oackages from order data based on URL parameter or manual input"""
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        order_number = None
        
        # Check which input triggered the load
        if trigger_id == 'load-order-btn' and manual_order:
            order_number = manual_order
            print(f"Loading order from manual input: {order_number}")
        elif trigger_id == 'url' and href:
            parsed = urlparse(href)
            params = parse_qs(parsed.query)
            order_number = params.get('order', [None])[0]
            print(f"Loading order from URL: {order_number}")
        
        if order_number:
            packages = create_demo_packages_for_order(order_number)
            return packages, len(packages)
        
        # If no order, return empty/default
        from config import INITIAL_PACKAGES
        return INITIAL_PACKAGES, len(INITIAL_PACKAGES)
    
    @app.callback(
        Output('url-order-info', 'children', allow_duplicate=True),
        [Input('load-order-btn', 'n_clicks'),
         State('order-input', 'value')],
        prevent_initial_call=True
    )
    def load_order_number(n_clicks, manual_order_number):
        """Change order number display in UI when clicking load button"""
        return html.Div([
                html.Span('📋 Order: ', style={'color': '#cbd5e1'}),
                html.Span(manual_order_number, style={'color': '#3b82f6', 'fontWeight': 'bold'}),
                html.Span(
                    f'', 
                    style={'color': '#94a3b8', 'fontSize': '12px', 'marginLeft': '5px'}
                )
            ])


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
            'weight': np.random.uniform(200, 400),
            'rotation': 0
        })
    
    return packages