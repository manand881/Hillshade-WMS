from datetime import datetime, timezone
from os import getenv
from os.path import abspath, dirname, join


class Config:
    """
    This class contains all the
    configuration variables for the application.
    """

    PROJECT_NAME = "Hillshade WMS"
    ROOT_DIR = dirname(dirname(abspath(__file__)))
    LOG_DIR = join(ROOT_DIR, "logs")
    DATA_DIR = join(ROOT_DIR, "data")

    TIMEZONE = timezone.utc
    STARTTIME = datetime.now(TIMEZONE)

    VERSION = getenv("VERSION", "1.0.0")
    DEBUG = getenv("DEBUG", True)
    WMS_CAPABILITIES = None

    WMS_RASTER_PATH = getenv("WMS_RASTER_PATH", "/tmp/dsm_clipped_cog.tif")
    WMS_PNG_PATH = None
    RASTER_NPY_PATH = WMS_RASTER_PATH.replace(".tif", ".npy")

    RASTER_MIN = None
    RASTER_MAX = None
    RASTER_NODATA = None
    RASTER_BLOCK_SIZE = None

    @classmethod
    def get_current_time(cls):
        return datetime.now(cls.TIMEZONE)
