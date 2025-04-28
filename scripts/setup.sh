#!/bin/bash

# Exit on error
set -e

echo "Setting up development environment..."

# Install Poetry if not present
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install Python dependencies
echo "Installing Python dependencies..."
poetry install

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
echo "  - Python tests: poetry run pytest"
echo "  - Node.js tests: npm test"
echo "  - PHP tests: ./vendor/bin/phpunit"
echo "  - Java tests: mvn test" 