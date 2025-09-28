import importlib
import re
from os.path import dirname, join

import pytest


def get_packages_from_requirements():
    """
    Read package names from requirements.txt and clean them for import.
    """
    requirements_path = join(dirname(dirname(__file__)), "requirements.txt")
    with open(requirements_path) as f:
        lines = [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.startswith("#")
        ]

    packages = []
    for line in lines:
        # Remove version specifiers and any other extras (e.g., package==1.0.0 -> package)
        # Also handle package names with hyphens by converting to underscores
        package_name = re.split(r"[<>=!~;\s]", line)[0].replace("-", "_")
        packages.append(package_name.lower())

    if "pytest" in packages:
        packages.remove("pytest")

    return packages


@pytest.mark.parametrize("package_name", get_packages_from_requirements())
def test_import_package(package_name):
    """
    Test that all required packages can be imported.
    """
    try:
        module = importlib.import_module(package_name)
        assert module is not None
    except ImportError as e:
        pytest.fail(f"Failed to import {package_name}: {str(e)}")
