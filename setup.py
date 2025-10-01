"""
Setup script for JobMiner.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jobminer",
    version="1.0.0",
    author="JobMiner Contributors",
    author_email="",
    description="A Python-based web scraping toolkit for extracting and organizing job listings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beingvirus/JobMiner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jobminer=jobminer_cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="web scraping, job listings, data extraction, automation",
    project_urls={
        "Bug Reports": "https://github.com/beingvirus/JobMiner/issues",
        "Source": "https://github.com/beingvirus/JobMiner",
        "Documentation": "https://github.com/beingvirus/JobMiner/blob/main/README.md",
    },
)
