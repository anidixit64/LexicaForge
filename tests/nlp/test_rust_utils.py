"""Unit tests for Rust-based string processing utilities."""

import pytest
from lexicaforge.nlp.utils.rust_utils import (
    StringProcessor,
    get_string_similarity,
    find_common_substrings,
    analyze_text,
)

def test_calculate_stats():
    """Test string statistics calculation."""
    text = "Hello, world!"
    stats = StringProcessor.calculate_stats(text)
    
    assert stats["char_count"] == 13
    assert stats["word_count"] == 2
    assert stats["unique_chars"] == 10
    assert stats["unique_words"] == 2
    assert stats["char_frequencies"]["l"] == 3
    assert stats["word_frequencies"]["Hello"] == 1
    assert stats["word_frequencies"]["world"] == 1

def test_levenshtein_distance():
    """Test Levenshtein distance calculation."""
    assert StringProcessor.levenshtein_distance("kitten", "sitting") == 3
    assert StringProcessor.levenshtein_distance("saturday", "sunday") == 3
    assert StringProcessor.levenshtein_distance("", "") == 0
    assert StringProcessor.levenshtein_distance("", "abc") == 3
    assert StringProcessor.levenshtein_distance("abc", "") == 3

def test_normalize_string():
    """Test string normalization."""
    assert StringProcessor.normalize_string("Hello, World!") == "hello, world!"
    assert StringProcessor.normalize_string("café") == "cafe"
    assert StringProcessor.normalize_string("über") == "uber"
    assert StringProcessor.normalize_string("") == ""

def test_find_patterns():
    """Test pattern matching."""
    text = "The quick brown fox jumps over the lazy dog"
    patterns = ["the", "fox", "dog"]
    
    matches = StringProcessor.find_patterns(text, patterns)
    
    assert "the" in matches
    assert "fox" in matches
    assert "dog" in matches
    assert len(matches["the"]) == 2
    assert len(matches["fox"]) == 1
    assert len(matches["dog"]) == 1

def test_process_batch():
    """Test batch text processing."""
    texts = [
        "Hello, world!",
        "Testing 123",
        "Another test",
    ]
    
    results = StringProcessor.process_batch(texts)
    
    assert len(results) == 3
    assert results[0]["word_count"] == 2
    assert results[1]["word_count"] == 2
    assert results[2]["word_count"] == 2

def test_tokenize():
    """Test text tokenization."""
    assert StringProcessor.tokenize("Hello, world!", ", ") == ["Hello", "world!"]
    assert StringProcessor.tokenize("one-two-three", "-") == ["one", "two", "three"]
    assert StringProcessor.tokenize("a.b.c", ".") == ["a", "b", "c"]
    assert StringProcessor.tokenize("", ",") == []

def test_get_string_similarity():
    """Test string similarity calculation."""
    assert get_string_similarity("kitten", "sitting") == pytest.approx(0.571, rel=1e-3)
    assert get_string_similarity("saturday", "sunday") == pytest.approx(0.625, rel=1e-3)
    assert get_string_similarity("", "") == 1.0
    assert get_string_similarity("", "abc") == 0.0
    assert get_string_similarity("abc", "") == 0.0

def test_find_common_substrings():
    """Test common substring finding."""
    s1 = "hello"
    s2 = "help"
    
    common = find_common_substrings(s1, s2, min_length=2)
    
    assert "hel" in common
    assert "he" in common
    assert "el" in common
    assert "lo" not in common

def test_analyze_text():
    """Test comprehensive text analysis."""
    text = "Hello, world! This is a test."
    analysis = analyze_text(text)
    
    assert analysis["char_count"] == 25
    assert analysis["word_count"] == 5
    assert analysis["unique_chars"] > 0
    assert analysis["unique_words"] == 5
    assert "Hello" in analysis["word_frequencies"]
    assert "world" in analysis["word_frequencies"]
    assert analysis["normalized_text"] == "hello, world! this is a test."
    assert len(analysis["tokens"]) == 5
    assert analysis["avg_word_length"] == pytest.approx(5.0, rel=1e-3)

def test_edge_cases():
    """Test edge cases and error handling."""
    # Empty string
    stats = StringProcessor.calculate_stats("")
    assert stats["char_count"] == 0
    assert stats["word_count"] == 0
    
    # Single character
    stats = StringProcessor.calculate_stats("a")
    assert stats["char_count"] == 1
    assert stats["word_count"] == 1
    
    # Whitespace only
    stats = StringProcessor.calculate_stats("   \t\n\r")
    assert stats["char_count"] == 5
    assert stats["word_count"] == 0
    
    # Special characters
    stats = StringProcessor.calculate_stats("!@#$%^&*()")
    assert stats["char_count"] == 10
    assert stats["word_count"] == 0
    
    # Unicode characters
    stats = StringProcessor.calculate_stats("café über")
    assert stats["char_count"] == 9
    assert stats["word_count"] == 2 