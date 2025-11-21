"""Main application entry point"""

import dash
from dash import Input, Output
from layout import create_layout
from callbacks import register_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Disable arrow key scrolling
app.clientside_callback(
    """
    function() {
        document.addEventListener('keydown', function(e) {
            if(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'PageUp', 'PageDown'].includes(e.key)) {
                e.preventDefault();
            }
        });
        return null;
    }
    """,
    Output('keyboard-event-store', 'data'),
    Input('keyboard-event-store', 'data')
)

app.layout = create_layout()
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8050) # debug = True