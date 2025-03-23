from typing import List, Tuple
import numpy as np


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        The Levenshtein distance between s1 and s2
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalized_levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Calculate normalized Levenshtein similarity between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Similarity score between 0 and 1, where 1 means identical
    """
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1 - (distance / max_len)


def get_consonant_skeleton(word: str) -> str:
    """
    Extract the consonant skeleton of a word by removing vowels.
    
    Args:
        word: Input word
        
    Returns:
        Consonant skeleton of the word
    """
    vowels = set('aeiouAEIOU')
    return ''.join(c for c in word if c not in vowels)


def align_sequences(s1: str, s2: str) -> Tuple[str, str, List[bool]]:
    """
    Align two sequences using dynamic programming.
    
    Args:
        s1: First sequence
        s2: Second sequence
        
    Returns:
        Tuple of (aligned s1, aligned s2, alignment mask)
    """
    m, n = len(s1), len(s2)
    dp = np.zeros((m + 1, n + 1))
    
    # Initialize the matrix
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j-1] + 1,  # substitution
                              dp[i-1][j] + 1,      # deletion
                              dp[i][j-1] + 1)      # insertion
    
    # Traceback to get alignment
    aligned1, aligned2 = [], []
    i, j = m, n
    alignment = []
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i-1] == s2[j-1]:
            aligned1.append(s1[i-1])
            aligned2.append(s2[j-1])
            alignment.append(True)
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i-1][j] + 1):
            aligned1.append(s1[i-1])
            aligned2.append('-')
            alignment.append(False)
            i -= 1
        else:
            aligned1.append('-')
            aligned2.append(s2[j-1])
            alignment.append(False)
            j -= 1
    
    aligned1.reverse()
    aligned2.reverse()
    alignment.reverse()
    
    return ''.join(aligned1), ''.join(aligned2), alignment 