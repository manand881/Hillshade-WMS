# Flask Backend API

A clean, minimal Flask backend API with essential configurations and error handling.

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the API Server

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Test the API using curl or a tool like Postman:
   ```bash
   # Health check endpoint
   curl http://localhost:5000/api/status
   ```

   Expected response:
   ```json
   {
     "service": "Flask Backend API",
     "status": "running",
     "timestamp": "2025-09-22T10:11:36.123456",
     "version": "1.0.0"
   }
   ```

## Project Structure

```
├── app.py                # Main application file with API endpoints
├── requirements.txt      # Python dependencies
└── .gitignore           # Git ignore file
```

## Development

- The application is set up with debug mode enabled by default.
- Any changes to Python files will automatically reload the server.
- Static files (CSS/JS) may require a hard refresh in your browser to see changes.

## License

This project is licensed under the MIT License.
For Docker deployment, you can use the provided Dockerfile and docker-compose.yml files.