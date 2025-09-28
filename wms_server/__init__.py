from flask import Flask, jsonify

from wms_server.settings import Config


def register_blueprints(app):
    """Register all blueprints with the Flask application.

    Args:
        app: Flask application instance
    """
    from .blueprints import blueprints

    for bp in blueprints:
        app.register_blueprint(bp)

    # Register error handlers that apply to the entire app
    @app.errorhandler(400)
    def bad_request(error):
        payload = {
            "error": "Bad Request",
            "message": (
                str(error)
                if str(error)
                else "The request could not be understood by the server"
            ),
        }
        return jsonify(payload), 400

    @app.errorhandler(404)
    def not_found(error):
        payload = {
            "error": "Not Found",
            "message": (
                str(error) if str(error) else "The requested resource was not found"
            ),
        }
        return jsonify(payload), 404

    @app.errorhandler(500)
    def server_error(error):
        payload = {
            "error": "Internal Server Error",
            "message": (
                str(error) if str(error) else "An internal server error occurred"
            ),
        }
        return jsonify(payload), 500


def create_app():
    """
    Application factory function to create and configure the Flask app
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    register_blueprints(app)

    return app
