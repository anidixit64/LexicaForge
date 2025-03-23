import pytest
from lexicaforge.nlp.utils.string_distance import (
    levenshtein_distance,
    normalized_levenshtein_similarity,
    get_consonant_skeleton,
    align_sequences
)


def test_levenshtein_distance():
    assert levenshtein_distance("", "") == 0
    assert levenshtein_distance("a", "") == 1
    assert levenshtein_distance("", "a") == 1
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("water", "wasser") == 3


def test_normalized_levenshtein_similarity():
    assert normalized_levenshtein_similarity("", "") == 1.0
    assert normalized_levenshtein_similarity("a", "") == 0.0
    assert normalized_levenshtein_similarity("", "a") == 0.0
    assert normalized_levenshtein_similarity("water", "water") == 1.0
    # "water" vs "wasser" has 3 operations needed, max length is 6
    assert normalized_levenshtein_similarity("water", "wasser") == 0.5


def test_get_consonant_skeleton():
    assert get_consonant_skeleton("") == ""
    assert get_consonant_skeleton("aeiou") == ""
    assert get_consonant_skeleton("water") == "wtr"
    assert get_consonant_skeleton("knight") == "knght"
    assert get_consonant_skeleton("psychology") == "psychlgy"


def test_align_sequences():
    # Test empty strings
    assert align_sequences("", "") == ("", "", [])
    
    # Test single character alignment
    aligned1, aligned2, mask = align_sequences("a", "a")
    assert aligned1 == "a"
    assert aligned2 == "a"
    assert mask == [True]
    
    # Test water/wasser alignment
    aligned1, aligned2, mask = align_sequences("water", "wasser")
    assert aligned1 == "wa-ter"
    assert aligned2 == "wasser"
    assert mask == [True, True, False, True, True, True]
    
    # Test different length strings
    aligned1, aligned2, mask = align_sequences("cat", "catch")
    assert aligned1 == "cat--"
    assert aligned2 == "catch"
    assert mask == [True, True, True, False, False] 