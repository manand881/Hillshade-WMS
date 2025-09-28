"""
Status Blueprint

This module provides health check and server status endpoints for monitoring
the WMS server's operational status.

Routes:
    GET /status - Returns the current server status and metadata
"""

import os

from flask import Blueprint, jsonify

from wms_server.settings import Config

#: The status blueprint handles server health and status endpoints.
#: All routes in this blueprint are prefixed with '/api'.
status_bp = Blueprint("status", __name__, url_prefix="/api")


@status_bp.route("/status", methods=["GET"])
def status():
    """
    Health check endpoint.

    Returns:
        JSON response containing:
        - status (str): Current server status ("running")
        - service (str): Name of the service
        - version (str): Current version of the service
        - timestamp (str): Current timestamp in ISO format
        - timezone (str): Server's timezone
        - uptime_seconds (float): Server uptime in seconds
        - cpu_count (int): Number of CPU cores available
    """
    current_time = Config.get_current_time()
    payload = {
        "status": "running",
        "service": Config.PROJECT_NAME,
        "version": Config.VERSION,
        "timestamp": current_time.isoformat(),
        "timezone": str(Config.TIMEZONE),
        "uptime_seconds": (current_time - Config.STARTTIME).total_seconds(),
        "cpu_count": os.cpu_count(),
    }
    return jsonify(payload), 200
