"""Setup script for LexicaForge."""

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
import subprocess
import sys
import os
from pathlib import Path

class RustBuildExt(build_ext):
    """Custom build extension for compiling Rust library."""
    
    def run(self):
        """Build the Rust library before running the normal build_ext."""
        rust_dir = Path(__file__).parent / "lexicaforge" / "rust"
        
        # Check if cargo is installed
        try:
            subprocess.run(["cargo", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Error: Cargo is not installed. Please install Rust and Cargo first.")
            print("Visit https://rustup.rs/ for installation instructions.")
            sys.exit(1)
        
        # Build the library
        try:
            subprocess.run(
                ["cargo", "build", "--release"],
                cwd=rust_dir,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print("Error building Rust library:")
            print(e.stderr.decode())
            sys.exit(1)
        
        # Run the normal build_ext
        build_ext.run(self)

setup(
    name="lexicaforge",
    version="0.1.0",
    description="A comprehensive etymology and linguistic analysis toolkit",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "graphql-core>=3.0.0",
        "sqlalchemy>=1.4.0",
        "pytest>=6.0.0",
        "pytest-cov>=2.0.0",
        "black>=21.0.0",
        "isort>=5.0.0",
        "mypy>=0.900",
        "flake8>=3.9.0",
    ],
    python_requires=">=3.8",
    cmdclass={
        "build_ext": RustBuildExt,
    },
    package_data={
        "lexicaforge": [
            "nlp/utils/*.so",  # Linux
            "nlp/utils/*.dylib",  # macOS
            "nlp/utils/*.dll",  # Windows
        ],
    },
    entry_points={
        "console_scripts": [
            "lexicaforge=lexicaforge.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
) 