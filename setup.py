from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="japanese_date_converter",
    version="1.0.0",
    author="Prateek Zare",
    author_email="prateezare@gmail.com",
    description="A simple tool to convert japanese-English-Japanese dates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prateekzare/japanese_date_converter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.x",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Japanese",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[],
    keywords="japanese, date, converter, era, reiwa, heisei, format",
    project_urls={
        "Bug Tracker": "https://github.com/prateekzare/japanese_date_converter/issues",
        "Documentation": "https://github.com/prateekzare/japanese_date_converter#readme",
        "Source Code": "https://github.com/prateekzare/japanese_date_converter",
    },
)