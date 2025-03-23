"""Python wrapper for Rust-based string processing utilities."""

from typing import Dict, List, Optional, Union
import lexicaforge_rust

class StringProcessor:
    """High-performance string processing utilities using Rust implementation."""
    
    @staticmethod
    def calculate_stats(text: str) -> Dict[str, Union[int, Dict[str, int]]]:
        """Calculate string statistics using Rust implementation.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Dictionary containing:
            - char_count: Total number of characters
            - word_count: Total number of words
            - unique_chars: Number of unique characters
            - unique_words: Number of unique words
            - char_frequencies: Dictionary of character frequencies
            - word_frequencies: Dictionary of word frequencies
        """
        return lexicaforge_rust.calculate_string_stats(text)
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Levenshtein distance between the strings
        """
        return lexicaforge_rust.levenshtein_distance(s1, s2)
    
    @staticmethod
    def normalize_string(s: str) -> str:
        """Normalize string for comparison.
        
        Args:
            s: Input string
            
        Returns:
            Normalized string (lowercase, decomposed Unicode)
        """
        return lexicaforge_rust.normalize_string(s)
    
    @staticmethod
    def find_patterns(text: str, patterns: List[str]) -> Dict[str, List[int]]:
        """Find all occurrences of patterns in text using Aho-Corasick algorithm.
        
        Args:
            text: Text to search in
            patterns: List of patterns to find
            
        Returns:
            Dictionary mapping patterns to lists of starting positions
        """
        return lexicaforge_rust.find_patterns(text, patterns)
    
    @staticmethod
    def process_batch(texts: List[str]) -> List[Dict[str, Union[int, Dict[str, int]]]]:
        """Process a batch of texts in parallel.
        
        Args:
            texts: List of texts to process
            
        Returns:
            List of string statistics for each text
        """
        return lexicaforge_rust.process_text_batch(texts)
    
    @staticmethod
    def tokenize(text: str, delimiters: str) -> List[str]:
        """Tokenize text using custom delimiters.
        
        Args:
            text: Text to tokenize
            delimiters: String of delimiter characters
            
        Returns:
            List of tokens
        """
        return lexicaforge_rust.tokenize(text, delimiters)

def get_string_similarity(s1: str, s2: str) -> float:
    """Calculate normalized string similarity between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Similarity score between 0 and 1
    """
    distance = StringProcessor.levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return 1.0 - (distance / max_len) if max_len > 0 else 1.0

def find_common_substrings(s1: str, s2: str, min_length: int = 2) -> List[str]:
    """Find common substrings between two strings.
    
    Args:
        s1: First string
        s2: Second string
        min_length: Minimum length of substrings to find
        
    Returns:
        List of common substrings
    """
    s1 = StringProcessor.normalize_string(s1)
    s2 = StringProcessor.normalize_string(s2)
    
    patterns = []
    for i in range(len(s1) - min_length + 1):
        for j in range(i + min_length, len(s1) + 1):
            patterns.append(s1[i:j])
    
    matches = StringProcessor.find_patterns(s2, patterns)
    return list(matches.keys())

def analyze_text(text: str) -> Dict[str, Union[int, float, List[str]]]:
    """Perform comprehensive text analysis.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary containing various text statistics and features
    """
    stats = StringProcessor.calculate_stats(text)
    normalized = StringProcessor.normalize_string(text)
    tokens = StringProcessor.tokenize(text, " \t\n\r.,!?;:()[]{}")
    
    return {
        "char_count": stats["char_count"],
        "word_count": stats["word_count"],
        "unique_chars": stats["unique_chars"],
        "unique_words": stats["unique_words"],
        "char_frequencies": stats["char_frequencies"],
        "word_frequencies": stats["word_frequencies"],
        "normalized_text": normalized,
        "tokens": tokens,
        "avg_word_length": stats["char_count"] / stats["word_count"] if stats["word_count"] > 0 else 0,
    } 