"""Main application entry point"""

import dash
from dash import Input, Output
from layout import create_layout
from callbacks import register_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Allow iframe embedding and fix CORS to implement to Power BI HTML Content
@app.server.after_request
def add_iframe_headers(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

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

# Set the layout
app.layout = create_layout()

# Register all callbacks
register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050) # debug = True