from flask import Flask, jsonify
from settings import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/api/status", methods=["GET"])
def status():
    """
    Health check endpoint
    Returns the current server status and timestamp in the configured timezone
    """
    current_time = Config.get_current_time()
    payload = {
        "status": "running",
        "service": Config.PROJECT_NAME,
        "version": Config.VERSION,
        "timestamp": current_time.isoformat(),
        "timezone": str(Config.TIMEZONE),
        "uptime_seconds": (current_time - Config.STARTTIME).total_seconds(),
    }
    return jsonify(payload), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=Config.DEBUG)
