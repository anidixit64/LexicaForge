# LexicaForge

A comprehensive natural language processing (NLP) toolkit designed for multilingual text analysis and processing. It provides a robust set of tools for text preprocessing, language detection, tokenization, and advanced NLP tasks, with a focus on scalability and performance through its integration with PySpark for distributed processing.

## Features

- Multilingual text preprocessing
- Language detection and validation
- Advanced tokenization
- Distributed processing with PySpark
- Comprehensive logging and monitoring
- Extensive test coverage
- Professional development practices

## Prerequisites

- Python 3.9 or higher
- Poetry (Python package manager)
- PostgreSQL (for development and testing)
- Java 8 or higher (for PySpark)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LexicaForge.git
cd LexicaForge
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install project dependencies:
```bash
poetry install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development Setup

1. Create and activate a virtual environment:
```bash
poetry shell
```

2. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

3. Set up the development database:
```bash
poetry run alembic upgrade head
```

## Usage

### Basic Text Processing

```python
from lexicaforge.core.text import TextProcessor
from lexicaforge.core.logging import logger

# Initialize the processor
processor = TextProcessor()

# Process text
text = "Hello, world! This is a sample text."
processed_text = processor.preprocess(text)

# Log the results
logger.info("Processed text", text=processed_text)
```

### Language Detection

```python
from lexicaforge.core.language import LanguageDetector

# Initialize the detector
detector = LanguageDetector()

# Detect language
text = "Bonjour le monde!"
language = detector.detect(text)
print(f"Detected language: {language}")
```

### Distributed Processing with PySpark

```python
from lexicaforge.core.spark import SparkProcessor
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("LexicaForge") \
    .getOrCreate()

# Create sample data
data = [("Hello world",), ("Bonjour le monde",)]
df = spark.createDataFrame(data, ["text"])

# Process data
processor = SparkProcessor()
result_df = processor.process_text(df, "text")

# Show results
result_df.show()
```

## Testing

Run the test suite:
```bash
poetry run pytest
```

Run with coverage report:
```bash
poetry run pytest --cov=lexicaforge
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PySpark for distributed processing capabilities
- spaCy for NLP features
- Polyglot for language detection
- All contributors and maintainers