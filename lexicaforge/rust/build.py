"""Build script for compiling the Rust library."""

import os
import subprocess
import sys
from pathlib import Path

def build_rust_library():
    """Build the Rust library using cargo."""
    rust_dir = Path(__file__).parent
    
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
    
    # Copy the compiled library to the Python package
    target_dir = rust_dir / "target" / "release"
    if sys.platform == "win32":
        lib_name = "lexicaforge_rust.dll"
    elif sys.platform == "darwin":
        lib_name = "liblexicaforge_rust.dylib"
    else:
        lib_name = "liblexicaforge_rust.so"
    
    lib_path = target_dir / lib_name
    if not lib_path.exists():
        print(f"Error: Compiled library not found at {lib_path}")
        sys.exit(1)
    
    # Create the Python package directory if it doesn't exist
    python_dir = rust_dir.parent / "nlp" / "utils"
    python_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the library to the Python package
    import shutil
    shutil.copy2(lib_path, python_dir / lib_name)
    
    print(f"Successfully built and installed {lib_name}")

if __name__ == "__main__":
    build_rust_library() 