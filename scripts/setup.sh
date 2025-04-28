#!/bin/bash

# Exit on error
set -e

echo "Setting up development environment..."

# Create and activate virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Install PHP dependencies
echo "Installing PHP dependencies..."
if ! command -v composer &> /dev/null; then
    echo "Composer not found. Please install Composer first."
    exit 1
fi
composer install

# Install Java dependencies
echo "Installing Java dependencies..."
if ! command -v mvn &> /dev/null; then
    echo "Maven not found. Please install Maven first."
    exit 1
fi
mvn install

echo "Setup complete! You can now run:"
echo "  - Python tests: pytest"
echo "  - Node.js tests: npm test"
echo "  - PHP tests: ./vendor/bin/phpunit"
echo "  - Java tests: mvn test"
echo ""
echo "To activate the Python virtual environment, run:"
echo "  source venv/bin/activate" 