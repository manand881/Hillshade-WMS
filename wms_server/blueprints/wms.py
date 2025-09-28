"""
WMS (Web Map Service) Blueprint

This module implements the OGC Web Map Service (WMS) 1.3.0 standard endpoints.
It provides capabilities for serving map images and metadata.

The service supports the following WMS operations:
- GetCapabilities: Returns service metadata in XML format
- GetMap: Returns a map image in PNG format
- GetFeatureInfo: Returns feature information (stub implementation)

The service is designed to work with single-band raster data and supports
both regular map visualization and hillshade rendering.

Routes:
    GET /wms - Main WMS service endpoint
    GET /wms?request=GetCapabilities - Returns service metadata
    GET /wms?request=GetMap - Returns a map image
    GET /wms?request=GetFeatureInfo - Returns feature information
"""

import xml.etree.ElementTree as ET
from os import remove
from os.path import join
from typing import Tuple, Union

from flask import Blueprint, Response, jsonify, make_response, request, send_file

from utils.logging import logger, request_logger_decorator
from utils.raster import (
    get_raster_crs,
    get_raster_extent,
    get_raster_stats,
    raster_to_png,
)
from wms_server.settings import Config

#: The WMS blueprint handles OGC Web Map Service endpoints
#: All routes in this blueprint are prefixed with '/wms'
wms_bp = Blueprint("wms", __name__, url_prefix="/wms")
get_raster_stats()
logger.info(f"WMS_RASTER_PATH: {Config.WMS_RASTER_PATH}")
logger.info(f"RASTER_BLOCK_SIZE: {Config.RASTER_BLOCK_SIZE}")


def fetch_capabilities(error: bool = False) -> str:
    """
    Fetch WMS capabilities from the data directory.

    Args:
        error: If True, loads the error capabilities template. Defaults to False.

    Returns:
        str: The contents of the capabilities XML file.
    """
    capabilities_path = join(Config.DATA_DIR, "capabilities.xml")
    if error:
        capabilities_path = join(Config.DATA_DIR, "capabilities_error.xml")
    with open(capabilities_path, "r") as f:
        return f.read()


def _get_capabilities_xml() -> str:
    """
    Generate WMS GetCapabilities XML response.

    Reads the base capabilities XML file and updates it with dynamic values
    such as the current server URL and raster extent.

    Returns:
        str: Formatted XML string containing the WMS capabilities.

    Note:
        Updates the Config.WMS_CAPABILITIES with the generated XML.
        Falls back to error template if generation fails.
    """
    try:
        # Read the capabilities XML file
        capabilities_xml = fetch_capabilities()

        # Parse the XML
        root = ET.fromstring(capabilities_xml)

        # Remove all namespace prefixes from element tags
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]  # Remove namespace prefix

        # Update the OnlineResource URLs with the current request URL
        base_url = request.url_root.rstrip("/")
        for elem in root.findall(".//OnlineResource"):
            if "type" in elem.attrib and elem.attrib["type"] == "simple":
                elem.set("{http://www.w3.org/1999/xlink}href", f"{base_url}/wms?")

        # Get the bounding box from the raster data
        original_bbox = get_raster_extent()
        raster_crs = get_raster_crs().to_string()

        crs_elem = root.findall(".//CRS")
        for elem in crs_elem:
            elem.text = raster_crs

        # Find and update the BoundingBox element
        bbox_elem = root.find(".//BoundingBox")
        if bbox_elem is not None:
            bbox_elem.set("minx", str(original_bbox[0]))
            bbox_elem.set("miny", str(original_bbox[1]))
            bbox_elem.set("maxx", str(original_bbox[2]))
            bbox_elem.set("maxy", str(original_bbox[3]))
            bbox_elem.set("CRS", raster_crs)

        # Create a new root with proper namespaces
        new_root = ET.Element(
            "WMS_Capabilities",
            {
                "xmlns": "http://www.opengis.net/wms",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://www.opengis.net/wms http://schemas.opengis.net/wms/1.3.0/capabilities_1_3_0.xsd",
                "version": "1.3.0",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
            },
        )

        # Move all children from old root to new root
        for child in root:
            new_root.append(child)

        # Convert to string with proper XML declaration
        xml_str = ET.tostring(new_root, encoding="utf-8", xml_declaration=True).decode(
            "utf-8"
        )

        # Ensure proper XML declaration
        if "<?xml" in xml_str:
            xml_str = (
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                + xml_str.split(">", 1)[1]
            )
        Config.WMS_CAPABILITIES = xml_str
        return xml_str

    except Exception as e:
        logger.error(f"Error generating capabilities XML: {str(e)}")
        return fetch_capabilities(error=True)


@wms_bp.route("", methods=["GET"])
@request_logger_decorator
def wms_service() -> Union[Response, Tuple[Response, int]]:
    """
    Main WMS service endpoint that handles all WMS requests.

    Query Parameters:
        request: The WMS request type (case-insensitive)
                - GetCapabilities: Returns service metadata
                - GetMap: Returns a map image
                - GetFeatureInfo: Returns feature information
        service: Must be 'WMS' (case-insensitive)
        version: WMS version (e.g., '1.3.0')
        BBOX: Bounding box for GetMap requests (format: "minx,miny,maxx,maxy")
        WIDTH: Width of the output image in pixels
        HEIGHT: Height of the output image in pixels
        LAYERS: Comma-separated list of layers to render
        FORMAT: Output format (e.g., 'image/png' for GetMap)

    Returns:
        Response:
            - For GetCapabilities: XML document
            - For GetMap: PNG image
            - For GetFeatureInfo: JSON response
            - Error responses in JSON format with appropriate status codes

    Raises:
        HTTP 400: For invalid or unsupported requests
        HTTP 404: If the requested resource is not found
        HTTP 500: For internal server errors
    """
    request_type = request.args.get("request", "").lower()

    if request_type == "":
        request_type = request.args.get("REQUEST", "").lower()

    logger.info(f"Request type: {request_type}")

    if request_type == "getcapabilities":
        # Return WMS capabilities XML
        xml = Config.WMS_CAPABILITIES or _get_capabilities_xml()
        response = make_response(xml)
        response.headers["Content-Type"] = "text/xml"
        return response

    elif request_type == "getmap":
        bbox = request.args.get("BBOX", "")
        width = request.args.get("WIDTH", "")
        height = request.args.get("HEIGHT", "")
        png_path = raster_to_png(bbox, width, height)

        try:
            return send_file(png_path, mimetype="image/png", as_attachment=False)
        except FileNotFoundError:
            error_response = {
                "error": "FileNotFound",
                "message": "Sample image not found",
                "path": Config.WMS_PNG_PATH,
            }
            return jsonify(error_response), 404
        finally:
            remove(png_path)

    elif request_type == "getfeatureinfo":
        # This would normally return feature information
        return jsonify(
            {
                "status": "success",
                "service": "WMS",
                "request": "GetFeatureInfo",
                "version": request.args.get("version", "1.3.0"),
                "x": request.args.get("x"),
                "y": request.args.get("y"),
                "i": request.args.get("i"),
                "j": request.args.get("j"),
                "query_layers": request.args.get("query_layers", "").split(","),
                "info_format": request.args.get("info_format", "application/json"),
                "feature_count": 0,
                "features": [],
            }
        )
    error_response = {
        "error": "InvalidRequest",
        "message": "Supported requests: GetCapabilities, GetMap, GetFeatureInfo. Received: {}".format(
            request_type or None
        ),
    }
    return jsonify(error_response), 400
