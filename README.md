# Hillshade Web Map Service (WMS)

A high-performance, containerized Web Map Service (WMS) implementation for serving hillshade raster data. This service implements the OGC WMS 1.3.0 standard, providing capabilities for serving map images and metadata with support for efficient raster data handling.

## Features

- **OGC WMS 1.3.0 Compliance**: Full support for standard WMS operations including GetCapabilities, GetMap, and GetFeatureInfo
- **On-the-Fly Tile Generation**: Generates map tiles dynamically for any requested extent and resolution without requiring pre-rendered tiles or disk caching
- **Efficient Raster Processing**: Optimized for handling large raster datasets with block-based processing
- **Docker Support**: Easy deployment using Docker
- **Cloud-Optimized GeoTIFF (COG) Support**: Built-in support for Cloud Optimized GeoTIFF format
- **Dynamic CRS Handling**: Automatic coordinate reference system detection and transformation
- **Performance Optimized**: Utilizes rasterio and numpy for fast image processing

## Assumptions

- The input raster is a Cloud Optimized GeoTIFF (COG)
- The input raster is available at the specified path and not in an s3/minio bucket
- It is acceptable to generate the hillshade to the scope of the current window
- The WMS client's CRS is set to the raster's CRS
- A colour ramp is not required for the generated tiles of either the hillshade or the elevation

## Prerequisites

- Docker and Docker Compose (for containerized deployment) or
- Python 3.13+
- GDAL (with development headers)
- pip (Python package manager)

## Quick Start with Docker

The easiest way to run the WMS server is using Docker:

```bash
docker-compose up -d
```

The service will be available at `http://localhost:8080/wms`

## Manual Installation

Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

Install system dependencies (Ubuntu/Debian example):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-dev gcc gdal-bin libgdal-dev
   ```

Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Configuration is handled through environment variables in the `wms_server/settings.py` file. Key configurations include:

- `WMS_RASTER_PATH`: Path to the input raster file (default: `data/sample.tif`)
- `DATA_DIR`: Directory containing additional data files (default: `data/`)
- `DEBUG`: Enable debug mode (default: `False`)

## Running the Server

### Using the Start Script (Recommended)

The easiest way to start the server is using the provided `start_server.sh` script:

```bash
# Make the script executable if needed
chmod +x start_server.sh

# Start the server in development mode
./start_server.sh

# Or for production mode
./start_server.sh --production
```

### Manual Startup

Alternatively, you can start the server manually:

1. Development server:
   ```bash
   python app.py
   ```

2. Production server with gunicorn:
   ```bash
   # use this command or your preferred configuration
   gunicorn -w 4 -b 0.0.0.0:8080 app:app
   ```

The WMS service will be available at `http://localhost:8080/wms`


### QGIS Setup

1. Go to `Layers` -> `Add Layer` -> `Add WMS/WMTS Layer`
2. Click on `New` to create a new WMS/WMTS server
3. Enter the URL of the WMS service - `http://localhost:8080/wms?service=WMS&version=1.3.0&request=GetCapabilities`
4. Click on `OK` to add the WMS/WMTS server
5. Click on `Connect` to connect to the WMS/WMTS server
6. Select the layer `hillshade` and click on `Add` to add the layer to the map


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

## Contributing

Contributions to the Hillshade-WMS project are welcome!

### Development Guidelines
- Follow the existing code style and formatting
- Write tests for new features and bug fixes(help needed)
- Update documentation as needed
- Ensure all tests pass before submitting a PR

### Development

- The application is set up with debug mode enabled by default.
- Any changes to Python files will automatically reload the server.
- The service includes built-in logging for monitoring and debugging.
- For production deployment, use the provided Dockerfile and docker-compose.yml for containerized deployment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.