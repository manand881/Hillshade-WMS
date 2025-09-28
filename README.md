# Hillshade Web Map Service (WMS)

A high-performance, containerized Web Map Service (WMS) implementation for serving hillshade raster data. This service implements the OGC WMS 1.3.0 standard, providing capabilities for serving map images and metadata with support for efficient raster data handling.

## Features

- **OGC WMS 1.3.0 Compliance**: Full support for standard WMS operations including GetCapabilities, GetMap, and GetFeatureInfo
- **Efficient Raster Processing**: Optimized for handling large raster datasets with block-based processing
- **Docker Support**: Easy deployment using Docker
- **Cloud-Optimized GeoTIFF (COG) Support**: Built-in support for Cloud Optimized GeoTIFF format
- **Dynamic CRS Handling**: Automatic coordinate reference system detection and transformation
- **Performance Optimized**: Utilizes rasterio and numpy for fast image processing

## Prerequisites

- Docker and Docker Compose (for containerized deployment) or
- Python 3.13+
- GDAL (with development headers)
- pip (Python package manager)

## Quick Start with Docker

The easiest way to run the WMS server is using Docker:

```bash
# Clone the repository
git clone <repository-url>
cd Hillshade-WMS

# Start the service
docker-compose up -d
```

The service will be available at `http://localhost:8080/wms`

## Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Hillshade-WMS
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install system dependencies (Ubuntu/Debian example):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-dev gcc gdal-bin libgdal-dev
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Configuration is handled through environment variables in the `wms_server/settings.py` file. Key configurations include:

- `WMS_RASTER_PATH`: Path to the input raster file (default: `data/sample.tif`)
- `DATA_DIR`: Directory containing additional data files (default: `data/`)
- `DEBUG`: Enable debug mode (default: `False`)

## Running the Server

1. Start the development server:
   ```bash
   python app.py
   ```
   Or use gunicorn for production:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8080 app:app
   ```

2. The WMS service will be available at `http://localhost:8080/wms`

## API Endpoints

### GetCapabilities
Returns the WMS service metadata in XML format.

```
GET /wms?request=GetCapabilities&service=WMS&version=1.3.0
```

### GetMap
Returns a map image for the specified parameters.

```
GET /wms?request=GetMap&layers=hillshade&styles=&crs=EPSG:3857&bbox=<minx>,<miny>,<maxx>,<maxy>&width=<width>&height=<height>&format=image/png&transparent=true
```

### GetFeatureInfo
Returns information about the feature at the specified location.

```
GET /wms?request=GetFeatureInfo&layers=hillshade&query_layers=hillshade&info_format=text/plain&x=<x>&y=<y>&width=<width>&height=<height>&bbox=<minx>,<miny>,<maxx>,<maxy>&crs=EPSG:3857
```

## Development

### Testing
Run the test suite with:
```bash
pytest tests/
```

### Linting and Code Style
This project uses pre-commit hooks for code quality. Install them with:
```bash
pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions to the Hillshade-WMS project! Here's how you can help:

1. **Fork** the repository to your own GitHub account
2. **Clone** the project to your local machine
3. **Create a feature branch** for your changes:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
4. **Commit** your changes with a clear, descriptive message:
   ```bash
   git commit -m 'feat: Add new feature or fix bug'
   ```
5. **Push** your changes to your fork:
   ```bash
   git push origin feature/YourFeatureName
   ```
6. Open a **Pull Request** with a clear description of your changes

### Development Guidelines
- Follow the existing code style and formatting
- Write tests for new features and bug fixes
- Update documentation as needed
- Ensure all tests pass before submitting a PR

## Development

- The application is set up with debug mode enabled by default.
- Any changes to Python files will automatically reload the server.
- The service includes built-in logging for monitoring and debugging.
- For production deployment, use the provided Dockerfile and docker-compose.yml for containerized deployment.
