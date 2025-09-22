from datetime import datetime, timezone
import os


class Config:
    """
    This class contains all the
    configuration variables for the application.
    """

    PROJECT_NAME = "Hillshade WMS"

    TIMEZONE = timezone.utc
    STARTTIME = datetime.now(TIMEZONE)

    VERSION = os.getenv("VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", True)


    @classmethod
    def get_current_time(cls):
        return datetime.now(cls.TIMEZONE)