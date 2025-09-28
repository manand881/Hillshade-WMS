"""
Blueprints package for the WMS server.

This package contains all the Flask blueprints that organize the application's
routes and functionality into logical components. Each blueprint represents
a distinct feature area of the application.

Blueprints in this package will be automatically registered with the Flask
application during initialization.

See the README.md in this directory for documentation on available blueprints
and how to add new ones.
"""

from wms_server.blueprints.status import status_bp
from wms_server.blueprints.wms import wms_bp

#: List of all blueprints that should be registered with the Flask application.
#: Add new blueprints to this list to have them automatically registered.
blueprints = [status_bp, wms_bp]
