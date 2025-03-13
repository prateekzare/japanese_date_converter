from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="japanese-date-converter",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive tool for converting between Japanese and standard date formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/japanese-date-converter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI