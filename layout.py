"""UI Layout for the truck loading application"""

from dash import dcc, html
from dash_extensions import EventListener
from config import INITIAL_PACKAGES, MOVE_STEP, TRUCK_LENGTH, TRUCK_WIDTH, TRUCK_HEIGHT
from visualization.figures import create_figure


def create_layout():
    """Create and return the main application layout"""
    return EventListener(
        id='keyboard-listener',
        events=[{"event": "keydown", "props": ["key", "shiftKey"]}],
        children=html.Div([
            html.Div([
                # Left panel - Controls
                create_control_panel(),
                
                # Right panel - 3D Visualization
                create_visualization_panel()
                
            ], style={'display': 'flex'}),
            
            *create_data_stores() # * = unpack each store as a seperate child - react thingy
            
        ], style={'margin': '0', 'padding': '0', 'fontFamily': 'Arial, sans-serif'}, tabIndex=-1)
    )


def create_control_panel():
    """Create the left control panel"""
    return html.Div([
        html.H2('🚛 Truck Loading Control', style={'marginBottom': '20px'}),
        
        html.Button(
            '➕ Add Package',
            id='add-package-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#3b82f6',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'marginBottom': '20px'
            }
        ),

        create_keyboard_shortcuts_info(),

        html.Div([
            html.H3('Summary', style={'marginBottom': '10px'}),
            html.Div(id='summary-stats')
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.H3('Packages', style={'marginBottom': '10px'}),
            html.Div(id='package-list', style={'maxHeight': '250px', 'overflowY': 'auto'})
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.H3('Edit Selected Package', style={'marginBottom': '10px'}),
            html.Div(id='package-controls')
        ], id='controls-container')
        
    ], style={
        'width': '350px',
        'padding': '20px',
        'backgroundColor': '#1e293b',
        'color': 'white',
        'height': '100vh',
        'overflowY': 'auto'
    })


def create_keyboard_shortcuts_info():
    """Create keyboard shortcuts information panel"""
    return html.Div([
        html.H3('⌨️ Keyboard Shortcuts', style={'marginBottom': '10px', 'fontSize': '16px'}),
        html.Div([
            html.Div('Arrow Keys: Move X/Y', style={'fontSize': '12px', 'color': '#cbd5e1', 'marginBottom': '3px'}),
            html.Div('PgUp/PgDn: Move Z', style={'fontSize': '12px', 'color': '#cbd5e1', 'marginBottom': '3px'}),
            html.Div('R: Rotate 90°', style={'fontSize': '12px', 'color': '#cbd5e1', 'marginBottom': '3px'}),
        ], style={'padding': '10px', 'backgroundColor': '#334155', 'borderRadius': '5px'})
    ], style={'marginBottom': '20px'})


def create_visualization_panel():
    """Create the right visualization panel"""
    return html.Div([
        dcc.Graph(
            id='truck-3d-graph',
            figure=create_figure(INITIAL_PACKAGES),
            style={'height': '100vh'}
        )
    ], style={'flex': '1'})


def create_data_stores():
    """Create data storage components"""
    return [
        dcc.Store(id='packages-store', data=INITIAL_PACKAGES),
        dcc.Store(id='selected-package-id', data=None),
        dcc.Store(id='package-counter', data=len(INITIAL_PACKAGES)),  
        dcc.Store(id='keyboard-event-store', data=None),
        dcc.Store(id='camera-store', data=None)
    ]