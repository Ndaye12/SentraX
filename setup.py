"""Setup script for SENTRAX"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="sentrax",
    version="3.1.0",
    author="Patrick Ndaye",
    author_email="patrickndaye919@gmail.com",
    description="Suite de cybersecurite professionnelle avec 10 scanners reseau",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ndaye12/sentrax",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sentrax=launcher:main",
            "sentrax-api=web.api:main",
        ],
    },
)