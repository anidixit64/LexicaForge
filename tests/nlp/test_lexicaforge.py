import pytest
from lexicaforge.nlp.lexicaforge import LexicaForge

@pytest.fixture
def nlp():
    return LexicaForge()

def test_tokenize(nlp):
    text = "Hello World! This is a test."
    tokens = nlp.tokenize(text)
    
    assert len(tokens) == 6
    assert tokens[0] == "hello"
    assert tokens[1] == "world!"
    assert tokens[2] == "this"
    assert tokens[3] == "is"
    assert tokens[4] == "a"
    assert tokens[5] == "test."

def test_tokenize_empty_string(nlp):
    text = ""
    tokens = nlp.tokenize(text)
    assert not tokens

def test_extract_entities(nlp):
    text = "John works at Google and Mary is at Microsoft"
    entities = nlp.extractEntities(text)
    
    assert len(entities) == 4
    assert "John" in entities
    assert "Google" in entities
    assert "Mary" in entities
    assert "Microsoft" in entities

def test_extract_entities_no_matches(nlp):
    text = "this is a test without proper nouns"
    entities = nlp.extractEntities(text)
    assert not entities

def test_calculate_similarity(nlp):
    text1 = "Hello World"
    text2 = "Hello Universe"
    similarity = nlp.calculateSimilarity(text1, text2)
    
    assert abs(similarity - 0.5) < 0.001

def test_calculate_similarity_identical(nlp):
    text = "Hello World"
    similarity = nlp.calculateSimilarity(text, text)
    assert abs(similarity - 1.0) < 0.001

def test_calculate_similarity_no_common(nlp):
    text1 = "Hello World"
    text2 = "Goodbye Universe"
    similarity = nlp.calculateSimilarity(text1, text2)
    assert abs(similarity - 0.0) < 0.001

def test_cache_functionality(nlp):
    text = "Test caching"
    
    # First call should compute
    tokens1 = nlp.tokenize(text)
    
    # Second call should use cache
    tokens2 = nlp.tokenize(text)
    
    assert tokens1 is tokens2  # Same object due to caching 