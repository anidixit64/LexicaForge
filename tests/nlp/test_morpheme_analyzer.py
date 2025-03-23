import pytest
from lexicaforge.nlp.morphemes.analyzer import MorphemeAnalyzer, Morpheme


@pytest.fixture
def analyzer():
    return MorphemeAnalyzer()


def test_find_prefix(analyzer):
    # Test known prefixes
    assert analyzer.find_prefix("unhappy") == Morpheme(
        text="un",
        type="prefix",
        meaning="not"
    )
    assert analyzer.find_prefix("rebuild") == Morpheme(
        text="re",
        type="prefix",
        meaning="again"
    )
    
    # Test case insensitivity
    assert analyzer.find_prefix("UNhappy") == Morpheme(
        text="un",
        type="prefix",
        meaning="not"
    )
    
    # Test no prefix
    assert analyzer.find_prefix("happy") is None


def test_find_suffix(analyzer):
    # Test known suffixes
    assert analyzer.find_suffix("happiness") == Morpheme(
        text="ness",
        type="suffix",
        meaning="state of being"
    )
    assert analyzer.find_suffix("walking") == Morpheme(
        text="ing",
        type="suffix",
        meaning="continuous action"
    )
    
    # Test case insensitivity
    assert analyzer.find_suffix("happiNESS") == Morpheme(
        text="ness",
        type="suffix",
        meaning="state of being"
    )
    
    # Test no suffix
    assert analyzer.find_suffix("happy") is None


def test_analyze_word(analyzer):
    # Test word with prefix and suffix
    morphemes = analyzer.analyze("unhappiness")
    assert len(morphemes) == 3
    assert morphemes[0] == Morpheme(text="un", type="prefix", meaning="not")
    assert morphemes[1] == Morpheme(text="happi", type="root")
    assert morphemes[2] == Morpheme(text="ness", type="suffix", meaning="state of being")
    
    # Test word with only prefix
    morphemes = analyzer.analyze("unhappy")
    assert len(morphemes) == 2
    assert morphemes[0] == Morpheme(text="un", type="prefix", meaning="not")
    assert morphemes[1] == Morpheme(text="happy", type="root")
    
    # Test word with only suffix
    morphemes = analyzer.analyze("happiness")
    assert len(morphemes) == 2
    assert morphemes[0] == Morpheme(text="happi", type="root")
    assert morphemes[1] == Morpheme(text="ness", type="suffix", meaning="state of being")
    
    # Test word with no affixes
    morphemes = analyzer.analyze("happy")
    assert len(morphemes) == 1
    assert morphemes[0] == Morpheme(text="happy", type="root")


def test_morpheme_frequency(analyzer):
    words = ["unhappy", "happiness", "rebuild", "building"]
    frequencies = analyzer.get_morpheme_frequency(words)
    
    assert frequencies["prefix"]["un"] == 1
    assert frequencies["prefix"]["re"] == 1
    assert frequencies["suffix"]["ness"] == 1
    assert frequencies["suffix"]["ing"] == 1
    assert "happy" in frequencies["root"]
    assert "build" in frequencies["root"]


def test_find_related_words(analyzer):
    word_list = ["unhappy", "happiness", "rebuild", "building", "cat"]
    related = analyzer.find_related_words("unhappiness", word_list)
    
    assert "happy" in related["happi"]
    assert "happiness" in related["happi"]
    assert "cat" not in str(related)  # cat should not be related to unhappiness


def test_edge_cases(analyzer):
    # Test empty string
    assert analyzer.analyze("") == []
    
    # Test single letter
    assert analyzer.analyze("a") == [Morpheme(text="a", type="root")]
    
    # Test word with multiple potential prefixes/suffixes
    # Should only match the first valid prefix/suffix
    morphemes = analyzer.analyze("reundoing")
    assert morphemes[0].text == "re"  # Should match 're' not 'un'
    assert morphemes[-1].text == "ing" 