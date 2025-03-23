from typing import List, Dict, Tuple
import numpy as np
from dataclasses import dataclass

from ..utils.string_distance import (
    normalized_levenshtein_similarity,
    get_consonant_skeleton,
    align_sequences
)


@dataclass
class CognateScore:
    """Data class for storing cognate detection scores."""
    word1: str
    word2: str
    similarity_score: float
    consonant_similarity: float
    alignment_score: float
    combined_score: float
    is_cognate: bool


class CognateDetector:
    """Class for detecting cognates between words."""
    
    def __init__(
        self,
        similarity_threshold: float = 0.7,
        consonant_weight: float = 0.4,
        alignment_weight: float = 0.3,
        levenshtein_weight: float = 0.3
    ):
        """
        Initialize the cognate detector.
        
        Args:
            similarity_threshold: Threshold for considering words as cognates
            consonant_weight: Weight for consonant skeleton similarity
            alignment_weight: Weight for sequence alignment score
            levenshtein_weight: Weight for Levenshtein similarity
        """
        self.similarity_threshold = similarity_threshold
        self.consonant_weight = consonant_weight
        self.alignment_weight = alignment_weight
        self.levenshtein_weight = levenshtein_weight
        
        assert np.isclose(
            consonant_weight + alignment_weight + levenshtein_weight,
            1.0
        ), "Weights must sum to 1.0"

    def calculate_alignment_score(self, s1: str, s2: str) -> float:
        """
        Calculate alignment score between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Alignment score between 0 and 1
        """
        _, _, alignment = align_sequences(s1, s2)
        if not alignment:
            return 0.0
        return sum(alignment) / len(alignment)

    def detect_cognates(self, word1: str, word2: str) -> CognateScore:
        """
        Detect if two words are cognates.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            CognateScore object with similarity scores and cognate status
        """
        # Calculate Levenshtein similarity
        levenshtein_sim = normalized_levenshtein_similarity(word1.lower(), word2.lower())
        
        # Calculate consonant skeleton similarity
        consonant1 = get_consonant_skeleton(word1.lower())
        consonant2 = get_consonant_skeleton(word2.lower())
        consonant_sim = normalized_levenshtein_similarity(consonant1, consonant2)
        
        # Calculate alignment score
        alignment_sim = self.calculate_alignment_score(word1.lower(), word2.lower())
        
        # Calculate combined score
        combined_score = (
            self.consonant_weight * consonant_sim +
            self.alignment_weight * alignment_sim +
            self.levenshtein_weight * levenshtein_sim
        )
        
        return CognateScore(
            word1=word1,
            word2=word2,
            similarity_score=levenshtein_sim,
            consonant_similarity=consonant_sim,
            alignment_score=alignment_sim,
            combined_score=combined_score,
            is_cognate=combined_score >= self.similarity_threshold
        )

    def find_potential_cognates(
        self,
        target_word: str,
        word_list: List[str],
        return_scores: bool = False
    ) -> List[Union[str, CognateScore]]:
        """
        Find potential cognates for a target word from a list of words.
        
        Args:
            target_word: Word to find cognates for
            word_list: List of words to search through
            return_scores: Whether to return CognateScore objects
            
        Returns:
            List of potential cognates or CognateScore objects
        """
        scores = [
            self.detect_cognates(target_word, word)
            for word in word_list
            if word != target_word
        ]
        
        cognates = [
            score for score in scores
            if score.is_cognate
        ]
        
        if return_scores:
            return sorted(cognates, key=lambda x: x.combined_score, reverse=True)
        
        return [score.word2 for score in sorted(
            cognates,
            key=lambda x: x.combined_score,
            reverse=True
        )] 