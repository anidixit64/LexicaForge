"""
High-performance morphological parser using Rust backend.
"""
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

try:
    from lexicaforge_parser import RustParser
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    logging.warning(
        "Rust parser not available. Using pure Python implementation. "
        "Install Rust and run 'maturin develop' in the rust_parser directory "
        "for better performance."
    )

@dataclass
class ParsedMorpheme:
    """Represents a parsed morpheme with its properties."""
    text: str
    morpheme_type: str
    position: int
    length: int
    meaning: Optional[str] = None

    def __post_init__(self):
        """Validate morpheme properties."""
        if not isinstance(self.position, int) or self.position < 0:
            raise ValueError("Position must be a non-negative integer")
        if not isinstance(self.length, int) or self.length <= 0:
            raise ValueError("Length must be a positive integer")
        if not self.text or len(self.text) != self.length:
            raise ValueError("Text length must match the specified length")


@dataclass
class ParsedWord:
    """Represents a parsed word with its morphological analysis."""
    original: str
    normalized: str
    morphemes: List[ParsedMorpheme]
    confidence: float

    def __post_init__(self):
        """Validate word analysis."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if not self.original:
            raise ValueError("Original word cannot be empty")
        if not self.normalized:
            raise ValueError("Normalized word cannot be empty")


class MorphologicalParser:
    """
    High-performance morphological parser with Rust backend.
    Falls back to pure Python implementation if Rust is not available.
    """
    
    def __init__(self):
        """Initialize the parser with the appropriate backend."""
        self._rust_parser = RustParser() if RUST_AVAILABLE else None
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize morpheme patterns."""
        # Common English prefixes
        self.prefixes = {
            'un': 'not',
            're': 'again',
            'dis': 'not, opposite of',
            'pre': 'before',
            'post': 'after',
            'anti': 'against',
            'sub': 'under',
            'inter': 'between',
            'trans': 'across',
            'super': 'above',
        }
        
        # Common English suffixes
        self.suffixes = {
            'ing': 'continuous action',
            'ed': 'past tense',
            'ly': 'in a manner of',
            'tion': 'act or process',
            'ment': 'state of',
            'ness': 'state of being',
            'able': 'capable of',
            'ible': 'capable of',
            'ful': 'full of',
            'less': 'without',
        }

        # Initialize Rust parser if available
        if self._rust_parser:
            self._rust_parser.initialize_patterns(self.prefixes, self.suffixes)

    @lru_cache(maxsize=1024)
    def parse_word(self, word: str) -> ParsedWord:
        """
        Parse a single word into its morphemes.
        
        Args:
            word: The word to parse
            
        Returns:
            ParsedWord object containing the analysis
            
        Raises:
            ValueError: If the word is invalid
        """
        if not word or not isinstance(word, str):
            raise ValueError("Word must be a non-empty string")

        if self._rust_parser:
            # Use Rust implementation
            result = self._rust_parser.batch_process([word])[0]
            return ParsedWord(
                original=result["original"],
                normalized=result["normalized"],
                morphemes=[
                    ParsedMorpheme(
                        text=m["text"],
                        morpheme_type=m["type"],
                        position=m["position"],
                        length=m["length"],
                        meaning=self.prefixes.get(m["text"]) or self.suffixes.get(m["text"])
                    )
                    for m in result["morphemes"]
                ],
                confidence=result["confidence"]
            )
        else:
            # Fallback to pure Python implementation
            return self._parse_word_python(word)

    def batch_parse(
        self,
        words: List[str],
        num_threads: Optional[int] = None
    ) -> List[ParsedWord]:
        """
        Parse multiple words in parallel.
        
        Args:
            words: List of words to parse
            num_threads: Optional number of threads to use
            
        Returns:
            List of ParsedWord objects
        """
        if not words:
            return []

        if self._rust_parser:
            # Use Rust's parallel implementation
            results = self._rust_parser.batch_process(words)
            return [
                ParsedWord(
                    original=r["original"],
                    normalized=r["normalized"],
                    morphemes=[
                        ParsedMorpheme(
                            text=m["text"],
                            morpheme_type=m["type"],
                            position=m["position"],
                            length=m["length"],
                            meaning=self.prefixes.get(m["text"]) or self.suffixes.get(m["text"])
                        )
                        for m in r["morphemes"]
                    ],
                    confidence=r["confidence"]
                )
                for r in results
            ]
        else:
            # Use Python's ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                return list(executor.map(self._parse_word_python, words))

    def _parse_word_python(self, word: str) -> ParsedWord:
        """
        Pure Python implementation of word parsing.
        Used as fallback when Rust is not available.
        """
        normalized = word.lower()
        morphemes = []
        confidence = 1.0
        current_pos = 0

        # Find prefix
        for prefix, meaning in self.prefixes.items():
            if normalized.startswith(prefix):
                morphemes.append(ParsedMorpheme(
                    text=prefix,
                    morpheme_type="prefix",
                    position=0,
                    length=len(prefix),
                    meaning=meaning
                ))
                current_pos = len(prefix)
                confidence *= 0.9
                break

        # Find suffix
        for suffix, meaning in self.suffixes.items():
            if normalized.endswith(suffix):
                pos = len(normalized) - len(suffix)
                morphemes.append(ParsedMorpheme(
                    text=suffix,
                    morpheme_type="suffix",
                    position=pos,
                    length=len(suffix),
                    meaning=meaning
                ))
                confidence *= 0.9
                break

        # Extract root
        root_end = next(
            (m.position for m in morphemes if m.morpheme_type == "suffix"),
            len(normalized)
        )
        if current_pos < root_end:
            root_text = normalized[current_pos:root_end]
            morphemes.append(ParsedMorpheme(
                text=root_text,
                morpheme_type="root",
                position=current_pos,
                length=len(root_text)
            ))

        return ParsedWord(
            original=word,
            normalized=normalized,
            morphemes=sorted(morphemes, key=lambda m: m.position),
            confidence=confidence
        ) 