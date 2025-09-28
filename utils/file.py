import tempfile
from os import makedirs
from os.path import dirname


def get_temp_file(extension: str) -> str:
    """
    Generate a temporary file path with the specified extension.

    Args:
        extension (str, optional): File extension (without the dot). Defaults to empty string.

    Returns:
        str: Path to a temporary file with the specified extension
    """
    # Create a temporary file with the specified extension
    NAME_PREFIX = "wms_tile_"
    SUFFIX = f".{extension.lstrip('.')}"

    with tempfile.NamedTemporaryFile(
        prefix=NAME_PREFIX, suffix=SUFFIX, delete=False
    ) as temp_file:
        temp_path = temp_file.name

    # Ensure the directory exists
    makedirs(dirname(temp_path), exist_ok=True)

    return temp_path
