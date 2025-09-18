"""
Setup script for WPBot - WhatsApp Bulk Sender
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wpbot",
    version="1.0.0",
    author="WPBot Team",
    author_email="",
    description="A Python application for sending bulk WhatsApp messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bilgehanyl/WPBot",  # Update with your actual repository URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wpbot=wpbot:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
