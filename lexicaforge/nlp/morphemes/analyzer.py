from typing import List, Dict, Set, Optional
from dataclasses import dataclass
import re
from collections import defaultdict

@dataclass
class Morpheme:
    """Data class for storing morpheme information."""
    text: str
    type: str  # 'prefix', 'root', 'suffix'
    meaning: Optional[str] = None
    language: Optional[str] = None


class MorphemeAnalyzer:
    """Class for analyzing morphemes in words."""
    
    def __init__(self):
        """Initialize the morpheme analyzer with common affixes."""
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
        
        # Compile regex patterns
        self.prefix_pattern = re.compile(
            f"^({'|'.join(self.prefixes.keys())})",
            re.IGNORECASE
        )
        self.suffix_pattern = re.compile(
            f"({'|'.join(self.suffixes.keys())})$",
            re.IGNORECASE
        )

    def find_prefix(self, word: str) -> Optional[Morpheme]:
        """Find a prefix in a word if it exists."""
        match = self.prefix_pattern.match(word)
        if match:
            prefix = match.group(0).lower()
            return Morpheme(
                text=prefix,
                type='prefix',
                meaning=self.prefixes[prefix]
            )
        return None

    def find_suffix(self, word: str) -> Optional[Morpheme]:
        """Find a suffix in a word if it exists."""
        match = self.suffix_pattern.search(word)
        if match:
            suffix = match.group(0).lower()
            return Morpheme(
                text=suffix,
                type='suffix',
                meaning=self.suffixes[suffix]
            )
        return None

    def extract_root(self, word: str, prefix: Optional[Morpheme], suffix: Optional[Morpheme]) -> Morpheme:
        """Extract the root morpheme from a word."""
        root_start = len(prefix.text) if prefix else 0
        root_end = -len(suffix.text) if suffix else None
        root_text = word[root_start:root_end]
        
        return Morpheme(
            text=root_text,
            type='root'
        )

    def analyze(self, word: str) -> List[Morpheme]:
        """
        Analyze a word and break it down into its constituent morphemes.
        
        Args:
            word: The word to analyze
            
        Returns:
            List of Morpheme objects representing the word's morphemes
        """
        morphemes = []
        
        # Find prefix
        prefix = self.find_prefix(word)
        if prefix:
            morphemes.append(prefix)
        
        # Find suffix
        suffix = self.find_suffix(word)
        if suffix:
            morphemes.append(suffix)
        
        # Extract root
        root = self.extract_root(word, prefix, suffix)
        if root.text:  # Only add if root is not empty
            # Insert root in the middle
            if prefix and suffix:
                morphemes.insert(1, root)
            else:
                morphemes.append(root)
        
        return morphemes

    def get_morpheme_frequency(self, words: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Calculate frequency of morphemes across a list of words.
        
        Args:
            words: List of words to analyze
            
        Returns:
            Dictionary mapping morpheme types to their frequencies
        """
        frequencies = defaultdict(lambda: defaultdict(int))
        
        for word in words:
            morphemes = self.analyze(word)
            for morpheme in morphemes:
                frequencies[morpheme.type][morpheme.text] += 1
        
        return dict(frequencies)

    def find_related_words(self, target_word: str, word_list: List[str]) -> Dict[str, List[str]]:
        """
        Find words that share morphemes with the target word.
        
        Args:
            target_word: Word to find relations for
            word_list: List of words to search through
            
        Returns:
            Dictionary mapping morpheme types to lists of related words
        """
        target_morphemes = self.analyze(target_word)
        related = defaultdict(list)
        
        for word in word_list:
            if word == target_word:
                continue
                
            word_morphemes = self.analyze(word)
            for t_morpheme in target_morphemes:
                for w_morpheme in word_morphemes:
                    if (t_morpheme.text == w_morpheme.text and 
                        t_morpheme.type == w_morpheme.type):
                        related[t_morpheme.text].append(word)
                        break
        
        return dict(related) 