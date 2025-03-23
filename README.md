# LexicaForge

A sophisticated etymology and cognate graph API that traces linguistic evolution across languages.

## Features

- GraphQL API for querying etymological relationships and cognate graphs
- Advanced NLP processing for cognate detection and morpheme analysis
- Scalable data processing pipeline using Apache Spark and Dagster
- PostgreSQL database with efficient graph querying capabilities
- Rust-powered performance-critical data parsing

## Tech Stack

- **Backend**: FastAPI + GraphQL (Strawberry)
- **Database**: PostgreSQL
- **Data Processing**: Apache Spark, Dagster
- **NLP**: Custom cognate detection, morpheme analysis
- **Performance**: Rust modules for critical operations

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Initialize the database:
```bash
poetry run alembic upgrade head
```

4. Run the development server:
```bash
poetry run uvicorn lexicaforge.api.main:app --reload
```

## Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Type checking: `poetry run mypy .`

## Project Structure

```
lexicaforge/
├── api/            # FastAPI + GraphQL implementation
├── db/             # Database models and migrations
├── etl/            # Data processing pipelines
├── nlp/            # NLP processing modules
└── tests/          # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT