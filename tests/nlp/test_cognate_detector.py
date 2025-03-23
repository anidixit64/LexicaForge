import pytest
from lexicaforge.nlp.cognates.detector import CognateDetector, CognateScore


@pytest.fixture
def detector():
    return CognateDetector(
        similarity_threshold=0.7,
        consonant_weight=0.4,
        alignment_weight=0.3,
        levenshtein_weight=0.3
    )


def test_cognate_detector_initialization():
    # Test default initialization
    detector = CognateDetector()
    assert detector.similarity_threshold == 0.7
    assert detector.consonant_weight == 0.4
    assert detector.alignment_weight == 0.3
    assert detector.levenshtein_weight == 0.3

    # Test custom initialization
    detector = CognateDetector(
        similarity_threshold=0.8,
        consonant_weight=0.5,
        alignment_weight=0.3,
        levenshtein_weight=0.2
    )
    assert detector.similarity_threshold == 0.8
    assert detector.consonant_weight == 0.5
    assert detector.alignment_weight == 0.3
    assert detector.levenshtein_weight == 0.2


def test_invalid_weights():
    with pytest.raises(AssertionError):
        CognateDetector(
            consonant_weight=0.5,
            alignment_weight=0.5,
            levenshtein_weight=0.5
        )


def test_detect_cognates(detector):
    # Test obvious cognates
    score = detector.detect_cognates("water", "wasser")
    assert score.is_cognate
    assert score.combined_score > 0.7
    assert score.word1 == "water"
    assert score.word2 == "wasser"

    # Test non-cognates
    score = detector.detect_cognates("water", "fire")
    assert not score.is_cognate
    assert score.combined_score < 0.7

    # Test identical words
    score = detector.detect_cognates("water", "water")
    assert score.is_cognate
    assert score.combined_score == 1.0


def test_find_potential_cognates(detector):
    word_list = ["water", "wasser", "eau", "fire", "wassir"]
    
    # Test without scores
    cognates = detector.find_potential_cognates("water", word_list)
    assert "wasser" in cognates
    assert "wassir" in cognates
    assert "eau" not in cognates
    assert "fire" not in cognates
    
    # Test with scores
    cognates = detector.find_potential_cognates("water", word_list, return_scores=True)
    assert all(isinstance(score, CognateScore) for score in cognates)
    assert len(cognates) >= 2
    assert cognates[0].combined_score >= cognates[1].combined_score  # Check sorting


def test_edge_cases(detector):
    # Test empty strings
    score = detector.detect_cognates("", "")
    assert score.combined_score == 1.0
    assert score.is_cognate

    # Test single character
    score = detector.detect_cognates("a", "a")
    assert score.combined_score == 1.0
    assert score.is_cognate

    # Test completely different strings
    score = detector.detect_cognates("xyz", "abc")
    assert score.combined_score < 0.7
    assert not score.is_cognate


def test_case_insensitivity(detector):
    score1 = detector.detect_cognates("water", "WATER")
    assert score1.is_cognate
    assert score1.combined_score == 1.0

    score2 = detector.detect_cognates("WaTeR", "wAtEr")
    assert score2.is_cognate
    assert score2.combined_score == 1.0 