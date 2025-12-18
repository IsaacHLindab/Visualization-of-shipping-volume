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
        
        # Summary stats
        html.Div([
            html.H3('Summary', style={'fontSize': '16px', 'marginBottom': '10px'}),
            html.Div(id='url-order-info', style={'marginBottom': '10px', 'color': '#cbd5e1'}),
            html.Div(id='summary-stats')
        ], style={'marginBottom': '20px', 'paddingBottom': '20px', 'borderBottom': '1px solid #475569'}),
        
        # Package list
        html.Div([
            html.H3('Packages', style={'fontSize': '16px', 'marginBottom': '10px'}),
            html.Button('➕ Add Package', id='add-package-btn', n_clicks=0,
                       style={'width': '100%', 'padding': '8px', 'marginBottom': '10px', 'cursor': 'pointer'}),
            html.Div(id='package-list', style={'maxHeight': '300px', 'overflowY': 'auto'})
        ], style={'marginBottom': '20px', 'paddingBottom': '20px', 'borderBottom': '1px solid #475569'}),
        
        # Edit controls
        html.Div([
            html.H3('Edit Package', style={'fontSize': '16px', 'marginBottom': '10px'}),
            html.Div(id='selected-package-name', 
                    children='Select a package to edit',
                    style={'color': '#94a3b8', 'marginBottom': '15px', 'fontStyle': 'italic'}),
            
            # Rotation
            html.Button('🔄 Rotate 90°', id='rotate-btn', n_clicks=0,
                       style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            
            # Grid
            create_floor_grid(),
            
            # Position sliders
            html.Div([
                html.Label('Position Controls:', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                
                # Auto-stack togle
                html.Div([
                    dcc.Checklist(
                        id='auto-stack-toggle',
                        options=[{'label': ' Smart stacking', 'value': 'enabled'}],
                        value=[],
                        style={'color': '#cbd5e1', 'fontSize': '12px'}
                    )
                ], style={'marginBottom': '10px'}),

                # X slider
                html.Div([
                    html.Div(id='x-position-display', children='X: --', 
                            style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='slider-x',
                        min=0,
                        max=TRUCK_LENGTH,
                        step=0.1,
                        value=0,
                        marks={0: '0m', TRUCK_LENGTH: f'{TRUCK_LENGTH}m'},
                        tooltip={"placement": "bottom", "always_visible": False},
                        disabled=True  # Disabled by default
                    )
                ], style={'marginBottom': '15px'}),
                
                # Y slider
                html.Div([
                    html.Div(id='y-position-display', children='Y: --',
                            style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='slider-y',
                        min=0,
                        max=TRUCK_WIDTH,
                        step=0.1,
                        value=0,
                        marks={0: '0m', TRUCK_WIDTH: f'{TRUCK_WIDTH}m'},
                        tooltip={"placement": "bottom", "always_visible": False},
                        disabled=True
                    )
                ], style={'marginBottom': '15px'}),
                
                # Z slider
                html.Div([
                    html.Div(id='z-position-display', children='Z: --',
                            style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='slider-z',
                        min=0,
                        max=TRUCK_HEIGHT,
                        step=0.1,
                        value=0,
                        marks={0: '0m', TRUCK_HEIGHT: f'{TRUCK_HEIGHT}m'},
                        tooltip={"placement": "bottom", "always_visible": False},
                        disabled=True
                    )
                ], style={'marginBottom': '15px'}),
            ], style={
                'padding': '15px',
                'backgroundColor': '#334155',
                'borderRadius': '5px',
                'marginBottom': '15px'
            }),

            # Dimension and weight controls
            html.Div([
                html.Label('Package Properties:', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                
                # Dimensions
                html.Div([
                    html.Label('Width (m):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-width',
                        type='number',
                        min=0.1,
                        max=TRUCK_LENGTH,
                        step=0.01,
                        placeholder='Width',
                        disabled=True,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '10px'}
                    )
                ]),
                
                html.Div([
                    html.Label('Depth (m):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-depth',
                        type='number',
                        min=0.1,
                        max=TRUCK_WIDTH,
                        step=0.01,
                        placeholder='Depth',
                        disabled=True,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '10px'}
                    )
                ]),
                
                html.Div([
                    html.Label('Height (m):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-height',
                        type='number',
                        min=0.1,
                        max=TRUCK_HEIGHT,
                        step=0.01,
                        placeholder='Height',
                        disabled=True,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '10px'}
                    )
                ]),
                
                html.Div([
                    html.Label('Weight (kg):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-weight',
                        type='number',
                        min=1,
                        max=10000,
                        step=1,
                        placeholder='Weight',
                        disabled=True,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '10px'}
                    )
                ]),

                html.Div([
                    html.Label(
                        [
                            dcc.Checklist(
                                id='input-stackable',
                                options=[{'label': ' Can be stacked on top', 'value': 'stackable'}],
                                value=[],
                                style={'color': '#cbd5e1'}
                            )
                        ],
                        style={'fontSize': '12px', 'marginBottom': '10px'}
                    )
                ], id='stackable-container', style={'display': 'none'})
                
            ], style={
                'padding': '15px',
                'backgroundColor': '#334155',
                'borderRadius': '5px',
                'marginBottom': '15px'
            }),

            # Quick align buttons
            html.Div([
                html.Label('Quick Align:', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Div([
                    html.Button('⬅️ Left', id='align-left-btn', n_clicks=0,
                               style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                    html.Button('➡️ Right', id='align-right-btn', n_clicks=0,
                               style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                ], style={'display': 'flex', 'marginBottom': '5px'}),
                html.Div([
                    html.Button('⬇️ Front', id='align-front-btn', n_clicks=0,
                               style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                    html.Button('⬆️ Back', id='align-back-btn', n_clicks=0,
                               style={'flex': '1', 'padding': '5px', 'fontSize': '11px', 'margin': '2px'}),
                ], style={'display': 'flex', 'marginBottom': '5px'}),
                html.Button('⬇️ Floor', id='align-floor-btn', n_clicks=0,
                           style={'width': '100%', 'padding': '5px', 'fontSize': '11px'})
            ], style={'marginBottom': '15px'}),
            
            # Truck dimensions
            html.Div([
                html.H3('🚛 Truck Dimensions', style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Div([
                    html.Label('Length (m):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-truck-length',
                        type='number',
                        min=4,
                        max=50,
                        step=0.01,
                        value=TRUCK_LENGTH,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '8px'}
                    )
                ]),
                html.Div([
                    html.Label('Width (m):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-truck-width',
                        type='number',
                        min=2,
                        max=10,
                        step=0.01,
                        value=TRUCK_WIDTH,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '8px'}
                    )
                ]),
                html.Div([
                    html.Label('Height (m):', style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '3px'}),
                    dcc.Input(
                        id='input-truck-height',
                        type='number',
                        min=2,
                        max=10,
                        step=0.01,
                        value=TRUCK_HEIGHT,
                        style={'width': '100%', 'padding': '5px', 'marginBottom': '8px'}
                    )
                ]),
                html.Button('Reset to Default', 
                            id='reset-truck-btn', 
                            n_clicks=0,
                            style={
                                'width': '100%',
                                'padding': '5px',
                                'fontSize': '11px',
                                'backgroundColor': '#475569',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '3px',
                                'cursor': 'pointer'
                            })
            ], style={'marginBottom': '20px', 'paddingBottom': '20px', 'borderBottom': '1px solid #475569'}),
        ], id='controls-container')
        
    ], id='control-panel', style={
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
        dcc.Location(id='url', refresh=False), # used to fetch transport order in url parameter
        dcc.Store(id='truck-dimensions', data={
            'length': TRUCK_LENGTH,
            'width': TRUCK_WIDTH,
            'height': TRUCK_HEIGHT
        })
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