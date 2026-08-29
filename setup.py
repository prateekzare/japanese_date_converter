"""
Compatibility shim. Real metadata lives in pyproject.toml.

Kept so that `pip install -e .` works on older pip/setuptools combinations
that still expect a setup.py to be present.
"""

from setuptools import setup

setup()
