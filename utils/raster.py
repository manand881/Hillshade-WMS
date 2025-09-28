import numpy as np
import rasterio
from PIL import Image
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

from utils.file import get_temp_file
from utils.logging import log_execution_time, logger
from wms_server.settings import Config


def get_raster_crs(raster_path: str = Config.WMS_RASTER_PATH) -> CRS:
    """
    Get CRS of a raster file.
    """
    with rasterio.open(raster_path) as src:
        crs = src.crs
    return crs


def get_raster_extent(raster_path: str = Config.WMS_RASTER_PATH) -> tuple:
    """
    Get extent of a raster file.
    """
    with rasterio.open(raster_path) as src:
        extent = src.bounds
    return extent


def get_raster_extent_wgs84(
    raster_path: str = Config.WMS_RASTER_PATH, target_crs: str = "EPSG:4326"
) -> tuple:
    """
    Get extent of a raster file in WGS84.

    Args:
        raster_path (str): Path to the raster file.
        target_crs (str): CRS to transform into (default: EPSG:4326).

    Returns:
        tuple: (min_lon, min_lat, max_lon, max_lat) in WGS84 (EPSG:4326).
    """
    src_crs = get_raster_crs(raster_path)
    bounds = get_raster_extent(raster_path)

    # Reproject bounds into WGS84
    return transform_bounds(src_crs, target_crs, *bounds, densify_pts=21)


@log_execution_time
def get_raster_stats(raster_path: str = Config.WMS_RASTER_PATH) -> None:
    """Get min/max statistics from a single-band raster, handling nodata values.

    Processes raster in blocks for memory efficiency. Only considers non-nodata values.

    Args:
        raster_path: Path to the single-band raster file.

    Returns:
        dict: {'nodata': value, 'min': min_value, 'max': max_value}
        Returns None for min/max if no valid data exists.

    Raises:
        FileNotFoundError: If raster file doesn't exist.
        ValueError: If raster is multi-band or invalid.
    """
    logger.info(f"Getting raster stats for {raster_path}")
    try:
        # Open the raster file
        with rasterio.open(raster_path) as src:
            # Verify single-band raster
            if src.count != 1:
                raise ValueError(
                    f"Expected a single-band raster, got {src.count} bands."
                )
            not_cog_conditions = [
                src.driver != "GTiff",
                not src.profile.get("tiled", False),
                not src.profile.get("blockxsize"),
                not src.profile.get("blockysize"),
                not src.overviews(1),
            ]
            if any(not_cog_conditions):
                raise ValueError("Input raster is not a valid COG.")

            Config.RASTER_BLOCK_SIZE = src.profile.get("blockxsize")

            # Get nodata value
            nodata = src.nodatavals[0]

            # Initialize min/max
            min_value = None
            max_value = None

            # Iterate over blocks
            for _, window in src.block_windows(1):  # Band 1
                # Read block
                block = src.read(1, window=window)

                # Mask nodata values
                if nodata is not None:
                    valid_data = block[block != nodata]
                else:
                    valid_data = block.flatten()

                del block
                # Update min/max if there is valid data
                if valid_data.size > 0:
                    block_min = float(np.min(valid_data))
                    block_max = float(np.max(valid_data))

                    # Update global min/max
                    if min_value is None or block_min < min_value:
                        min_value = block_min
                    if max_value is None or block_max > max_value:
                        max_value = block_max

            Config.RASTER_MIN = min_value
            Config.RASTER_MAX = max_value
            Config.RASTER_NODATA = nodata

        if Config.RASTER_MIN is None or Config.RASTER_MAX is None:
            raise ValueError("Failed to calculate min/max values for the raster.")
        if Config.RASTER_MIN == Config.RASTER_MAX:
            raise ValueError("Min and max values are equal for the raster.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Raster file not found: {raster_path}")
    except Exception as e:
        raise ValueError(f"Error processing raster: {str(e)}")


def raster_to_png(bbox: str, width: int, height: int) -> str:
    """
    Clip single-band raster to bbox and convert to PNG. Returns path to the PNG file.

    Args:
        bbox (str): Bounding box in format "minx,miny,maxx,maxy" in the raster's CRS.
                    If empty, uses the full extent of the raster.

    Returns:
        str: Path to the generated PNG file

    Raises:
        ValueError: If the raster is not single-band or if bbox is invalid
        IOError: If there's an error reading the raster or saving the PNG
    """
    raster_path = Config.WMS_RASTER_PATH
    png_path = get_temp_file("png")
    global_min = Config.RASTER_MIN
    global_max = Config.RASTER_MAX
    nodata = Config.RASTER_NODATA
    width = int(width)
    height = int(height)

    try:
        minx, miny, maxx, maxy = map(float, bbox.split(","))
    except Exception:
        raise ValueError("Invalid bbox format. Use 'minx,miny,maxx,maxy'.")

    try:
        with rasterio.open(raster_path) as src:

            window = from_bounds(minx, miny, maxx, maxy, transform=src.transform)
            window = window.round_offsets().round_lengths()
            data = src.read(
                1,
                window=window,
                out_shape=(int(height), int(width)),
                resampling=Resampling.bilinear,
            )

        data = data.astype(float)
        mask_nodata = data == nodata  # True where nodata
        data[data == nodata] = global_min

        # Normalize data to 0–255 ignoring nan using global min and max
        data_norm = (data - global_min) / (global_max - global_min) * 255

        # Reset nodata positions to NaN before casting
        data_norm = np.clip(data_norm, 0, 255).astype(np.uint8)

        # Create RGBA image with transparency for nodata pixels
        alpha = np.where(mask_nodata, 0, 255).astype(np.uint8)

        del mask_nodata
        del data

        image = Image.fromarray(data_norm, mode="L")
        image.putalpha(Image.fromarray(alpha, mode="L"))
        resized_image = image.resize((width, height), Image.Resampling.BILINEAR)
        resized_image.save(png_path)

        return png_path

    except Exception as e:
        raise IOError(f"Error processing raster: {e}")
