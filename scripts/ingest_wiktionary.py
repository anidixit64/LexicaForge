#!/usr/bin/env python3
"""Script to ingest data from Wiktionary."""

import asyncio
import argparse
from pathlib import Path

from lexicaforge.data.ingestion.wiktionary import WiktionaryIngester
from lexicaforge.core.logging import configure_logging, logger

async def main():
    """Main function to run the Wiktionary data ingestion."""
    parser = argparse.ArgumentParser(description="Ingest data from Wiktionary")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/wiktionary"),
        help="Directory to store ingested data"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        help="List of language codes to ingest"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of words to process in each batch"
    )
    args = parser.parse_args()

    # Configure logging
    configure_logging(
        log_level="INFO",
        log_file=args.output_dir / "ingestion.log",
        development=True
    )

    logger.info("Starting Wiktionary data ingestion")
    
    async with WiktionaryIngester(
        output_dir=args.output_dir,
        languages=args.languages,
        batch_size=args.batch_size
    ) as ingester:
        # Get list of words to process
        words = await ingester.get_word_list()
        logger.info(f"Found {len(words)} words to process")

        # Process words
        results = await ingester.ingest_words(words)
        logger.info(f"Successfully processed {len(results)} words")

if __name__ == "__main__":
    asyncio.run(main()) 