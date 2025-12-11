"""Callback modules for the truck loading application"""
from . import package_callbacks
from . import ui_callbacks
from . import url_callbacks

def register_callbacks(app):
    """Register all callbacks with the Dash app"""
    package_callbacks.register_callbacks(app)
    ui_callbacks.register_callbacks(app)
    url_callbacks.register_callbacks(app)