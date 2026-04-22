"""
This module creates and initializes the Shiny application by connecting
the user interface and server components into a single app instance.
"""

from shiny import App
from frontend import app_ui
from backend import server

"""
Creates the Shiny application object that represents the complete
interactive application composed of the defined user interface
and server logic.
"""
app = App(app_ui, server)
