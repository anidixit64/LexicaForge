#!/usr/bin/env python3
"""Development environment setup script for LexicaForge.

This script helps developers set up their development environment by:
1. Installing pre-commit hooks
2. Setting up logging configuration
3. Creating necessary directories
4. Initializing development configuration
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

def run_command(command: list[str], cwd: Path | None = None) -> bool:
    """Run a shell command and return True if successful.
    
    Args:
        command: The command to run as a list of strings
        cwd: Optional working directory for the command
        
    Returns:
        bool: True if the command succeeded, False otherwise
    """
    try:
        subprocess.run(command, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e}", file=sys.stderr)
        return False

def setup_development_environment() -> bool:
    """Set up the development environment.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Create necessary directories
    directories = [
        project_root / "logs",
        project_root / "data",
        project_root / ".vscode"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
    
    # Install pre-commit hooks
    if not run_command(["pre-commit", "install"], cwd=project_root):
        return False
    
    # Run pre-commit hooks on all files
    if not run_command(["pre-commit", "run", "--all-files"], cwd=project_root):
        return False
    
    # Create .env file if it doesn't exist
    env_file = project_root / ".env"
    if not env_file.exists():
        env_example = project_root / ".env.example"
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("Created .env file from .env.example")
    
    # Load environment variables
    load_dotenv(env_file)
    
    print("Development environment setup completed successfully!")
    return True

if __name__ == "__main__":
    if not setup_development_environment():
        sys.exit(1) 