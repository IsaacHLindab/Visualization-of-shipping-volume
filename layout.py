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
    # Read the id of each element for a description of what it is used for

    return html.Div([
        html.H2('🚛 Truck Loading Control', style={'marginBottom': '20px'}),
        
        html.Div([
            html.Label('Order Number:', style={
                'fontSize': '14px', 
                'marginBottom': '5px',
                'display': 'block',
                'fontWeight': 'bold'
            }),
            html.Div([
                dcc.Input(
                    id='order-input',
                    type='text',
                    placeholder='Enter order number...',
                    style={
                        'width': '70%',
                        'padding': '8px',
                        'borderRadius': '5px',
                        'border': '1px solid #475569',
                        'backgroundColor': '#334155',
                        'color': 'white',
                        'marginRight': '5px'
                    }
                ),
                html.Button(
                    '🔍 Load',
                    id='load-order-btn',
                    n_clicks=0,
                    style={
                        'padding': '8px 15px',
                        'backgroundColor': '#10b981',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '14px'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'padding': '15px',
            'backgroundColor': '#334155',
            'borderRadius': '5px',
            'marginBottom': '20px'
        }),

        html.Div(
            id='url-order-info',
            style={
                'padding': '10px',
                'backgroundColor': '#334155',
                'borderRadius': '5px',
                'marginBottom': '20px',
                'fontSize': '14px',
                'fontWeight': 'bold'
            }
        ),

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

        html.Div([
            html.H3('Summary', style={'marginBottom': '10px'}),
            html.Div(id='summary-stats')
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.H3('Packages', style={'marginBottom': '10px'}),
            html.Div(id='package-list', style={'maxHeight': '250px', 'overflowY': 'auto'})
        ], style={'marginBottom': '20px'}),

        create_floor_grid(),
        
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
    """ 
    Create data storage components 
    Per session (dissapears if refresh)
    todo: cache data
    """
    return [
        dcc.Store(id='packages-store', data=INITIAL_PACKAGES),
        dcc.Store(id='selected-package-id', data=None),
        dcc.Store(id='package-counter', data=len(INITIAL_PACKAGES)),  
        dcc.Store(id='keyboard-event-store', data=None), # register keyboard events
        dcc.Store(id='camera-store', data=None), # store camera position inbetween renders
        dcc.Location(id='url', refresh=False) # used to fetch transport order in url parameter
    ]

def create_floor_grid():
    """Create clickable grid for quick positioning"""
    from config import TRUCK_LENGTH, TRUCK_WIDTH
    
    # Grid configuration
    cell_width = 1.0
    cols = int(TRUCK_LENGTH / cell_width)
    rows = int(TRUCK_WIDTH / cell_width)
    
    grid_cells = []
    for row in range(rows):
        row_cells = []
        for col in range(cols):
            cell_x = col * cell_width
            cell_y = row * cell_width
            
            row_cells.append(
                html.Div(
                    id={'type': 'grid-cell', 'x': cell_x, 'y': cell_y},
                    style={
                        'width': '30px',
                        'height': '50px',
                        'border': '1px solid #475569',
                        'backgroundColor': '#1e293b',
                        'cursor': 'pointer',
                        'transition': 'background-color 0.2s'
                    },
                    n_clicks=0
                )
            )
        
        grid_cells.append(
            html.Div(row_cells, style={'display': 'flex'})
        )
    
    return html.Div([
        html.Label('Quick Position (Click Grid):', 
                  style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        html.Div(grid_cells, style={
            'border': '2px solid #475569',
            'padding': '5px',
            'borderRadius': '5px',
            'marginBottom': '15px'
        }),
        html.Div('Click a cell to position package', 
                style={'fontSize': '11px', 'color': '#94a3b8', 'textAlign': 'center'})
    ])