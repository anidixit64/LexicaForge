"""Unit tests for the morphological parser."""
import pytest
from lexicaforge.nlp.parser import (
    MorphologicalParser,
    ParsedWord,
    ParsedMorpheme,
    RUST_AVAILABLE
)


@pytest.fixture
def parser():
    """Create a parser instance for testing."""
    return MorphologicalParser()


def test_parsed_morpheme_validation():
    """Test ParsedMorpheme validation."""
    # Valid morpheme
    morpheme = ParsedMorpheme(
        text="un",
        morpheme_type="prefix",
        position=0,
        length=2,
        meaning="not"
    )
    assert morpheme.text == "un"
    assert morpheme.length == 2

    # Invalid position
    with pytest.raises(ValueError):
        ParsedMorpheme(
            text="un",
            morpheme_type="prefix",
            position=-1,  # Invalid
            length=2
        )

    # Invalid length
    with pytest.raises(ValueError):
        ParsedMorpheme(
            text="un",
            morpheme_type="prefix",
            position=0,
            length=0  # Invalid
        )

    # Mismatched text length
    with pytest.raises(ValueError):
        ParsedMorpheme(
            text="un",
            morpheme_type="prefix",
            position=0,
            length=3  # Doesn't match text length
        )


def test_parsed_word_validation():
    """Test ParsedWord validation."""
    # Valid word
    word = ParsedWord(
        original="unhappy",
        normalized="unhappy",
        morphemes=[
            ParsedMorpheme(text="un", morpheme_type="prefix", position=0, length=2),
            ParsedMorpheme(text="happy", morpheme_type="root", position=2, length=5)
        ],
        confidence=0.9
    )
    assert word.original == "unhappy"
    assert len(word.morphemes) == 2

    # Invalid confidence
    with pytest.raises(ValueError):
        ParsedWord(
            original="unhappy",
            normalized="unhappy",
            morphemes=[],
            confidence=1.5  # Invalid
        )

    # Empty original word
    with pytest.raises(ValueError):
        ParsedWord(
            original="",  # Invalid
            normalized="unhappy",
            morphemes=[],
            confidence=0.9
        )


def test_single_word_parsing(parser):
    """Test parsing individual words."""
    # Test word with prefix
    result = parser.parse_word("unhappy")
    assert result.original == "unhappy"
    assert result.normalized == "unhappy"
    assert len(result.morphemes) >= 2
    assert any(m.morpheme_type == "prefix" and m.text == "un" for m in result.morphemes)
    assert any(m.morpheme_type == "root" for m in result.morphemes)

    # Test word with suffix
    result = parser.parse_word("happiness")
    assert result.original == "happiness"
    assert any(m.morpheme_type == "suffix" and m.text == "ness" for m in result.morphemes)

    # Test word with both prefix and suffix
    result = parser.parse_word("unhappiness")
    assert len(result.morphemes) >= 3
    assert any(m.morpheme_type == "prefix" and m.text == "un" for m in result.morphemes)
    assert any(m.morpheme_type == "suffix" and m.text == "ness" for m in result.morphemes)
    assert any(m.morpheme_type == "root" for m in result.morphemes)

    # Test simple word
    result = parser.parse_word("cat")
    assert len(result.morphemes) == 1
    assert result.morphemes[0].morpheme_type == "root"

    # Test invalid input
    with pytest.raises(ValueError):
        parser.parse_word("")


def test_batch_parsing(parser):
    """Test batch parsing functionality."""
    words = ["unhappy", "happiness", "cat", "walking"]
    results = parser.batch_parse(words)

    assert len(results) == 4
    assert all(isinstance(r, ParsedWord) for r in results)
    assert [r.original for r in results] == words

    # Test empty input
    assert parser.batch_parse([]) == []

    # Test parallel processing
    results_threaded = parser.batch_parse(words, num_threads=2)
    assert len(results_threaded) == 4
    assert all(isinstance(r, ParsedWord) for r in results_threaded)


def test_morpheme_ordering(parser):
    """Test that morphemes are correctly ordered by position."""
    result = parser.parse_word("unhappiness")
    positions = [m.position for m in result.morphemes]
    assert positions == sorted(positions)


def test_confidence_scoring(parser):
    """Test confidence score calculation."""
    # Word with no affixes should have high confidence
    result = parser.parse_word("cat")
    assert result.confidence == 1.0

    # Words with affixes should have lower confidence
    result = parser.parse_word("unhappy")
    assert result.confidence < 1.0

    result = parser.parse_word("unhappiness")
    assert result.confidence < 1.0  # Even lower due to multiple affixes


@pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust parser not available")
def test_rust_implementation(parser):
    """Test Rust implementation specifically."""
    assert parser._rust_parser is not None
    
    # Test that Rust parser gives same results as Python
    word = "unhappiness"
    rust_result = parser.parse_word(word)
    parser._rust_parser = None  # Force Python implementation
    python_result = parser._parse_word_python(word)
    
    assert rust_result.original == python_result.original
    assert rust_result.normalized == python_result.normalized
    assert len(rust_result.morphemes) == len(python_result.morphemes)
    
    for r_morph, p_morph in zip(rust_result.morphemes, python_result.morphemes):
        assert r_morph.text == p_morph.text
        assert r_morph.morpheme_type == p_morph.morpheme_type
        assert r_morph.position == p_morph.position 