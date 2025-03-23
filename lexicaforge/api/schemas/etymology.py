from typing import List, Optional, Dict
import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session

from lexicaforge.db.models.etymology import Language as LanguageModel
from lexicaforge.db.models.etymology import Word as WordModel
from lexicaforge.db.models.etymology import Etymology as EtymologyModel
from lexicaforge.db.models.etymology import LanguageFamily
from lexicaforge.db.config import get_db
from lexicaforge.nlp.cognates.detector import CognateDetector, CognateScore
from lexicaforge.nlp.morphemes.analyzer import MorphemeAnalyzer, Morpheme as MorphemeModel


@strawberry.enum
class LanguageFamilyEnum(LanguageFamily):
    pass


@strawberry.type
class Language:
    id: int
    name: str
    code: str
    family: LanguageFamilyEnum

    @strawberry.field
    def words(self, info: Info) -> List["Word"]:
        db: Session = info.context["db"]
        return db.query(WordModel).filter(WordModel.language_id == self.id).all()


@strawberry.type
class Word:
    id: int
    text: str
    pronunciation: Optional[str]
    definition: Optional[str]
    language: Language

    @strawberry.field
    def etymologies(self, info: Info) -> List["Etymology"]:
        db: Session = info.context["db"]
        return db.query(EtymologyModel).filter(EtymologyModel.word_id == self.id).all()

    @strawberry.field
    def cognates(self, info: Info) -> List["Word"]:
        db: Session = info.context["db"]
        word = db.query(WordModel).get(self.id)
        return word.cognates if word else []


@strawberry.type
class Etymology:
    id: int
    word: Word
    ancestor: Optional[Word]
    relationship_type: str
    confidence_score: Optional[int]
    notes: Optional[str]


@strawberry.type
class CognateResult:
    word: str
    similarity_score: float
    is_cognate: bool
    confidence: float


@strawberry.type
class Morpheme:
    text: str
    type: str
    meaning: Optional[str]


@strawberry.type
class MorphemeAnalysis:
    word: str
    morphemes: List[Morpheme]
    related_words: List[str]


@strawberry.type
class Query:
    @strawberry.field
    def languages(self, info: Info) -> List[Language]:
        db: Session = info.context["db"]
        return db.query(LanguageModel).all()

    @strawberry.field
    def word(self, info: Info, id: int) -> Optional[Word]:
        db: Session = info.context["db"]
        return db.query(WordModel).get(id)

    @strawberry.field
    def search_words(self, info: Info, text: str, language_code: Optional[str] = None) -> List[Word]:
        db: Session = info.context["db"]
        query = db.query(WordModel).filter(WordModel.text.ilike(f"%{text}%"))
        if language_code:
            query = query.join(LanguageModel).filter(LanguageModel.code == language_code)
        return query.all()

    @strawberry.field
    def detect_cognates(
        self,
        info: Info,
        word: str,
        target_language_code: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[CognateResult]:
        """
        Detect potential cognates for a given word.
        
        Args:
            word: The word to find cognates for
            target_language_code: Optional language code to restrict search
            min_confidence: Minimum confidence score for cognate detection
            
        Returns:
            List of potential cognates with their scores
        """
        db: Session = info.context["db"]
        
        # Get all words from the target language
        query = db.query(WordModel)
        if target_language_code:
            query = query.join(LanguageModel).filter(
                LanguageModel.code == target_language_code
            )
        
        # Get word texts for cognate detection
        word_list = [w.text for w in query.all()]
        
        # Initialize cognate detector with custom threshold
        detector = CognateDetector(similarity_threshold=min_confidence)
        
        # Get cognate scores
        cognate_scores = detector.find_potential_cognates(
            word,
            word_list,
            return_scores=True
        )
        
        # Convert to GraphQL type
        return [
            CognateResult(
                word=score.word2,
                similarity_score=score.similarity_score,
                is_cognate=score.is_cognate,
                confidence=score.combined_score
            )
            for score in cognate_scores
        ]

    @strawberry.field
    def analyze_morphemes(
        self,
        info: Info,
        word: str,
        find_related: bool = False
    ) -> MorphemeAnalysis:
        """
        Analyze the morphemes in a word.
        
        Args:
            word: The word to analyze
            find_related: Whether to search for related words in the database
            
        Returns:
            MorphemeAnalysis object with morphemes and optionally related words
        """
        analyzer = MorphemeAnalyzer()
        morphemes = analyzer.analyze(word)
        
        related_words = []
        if find_related:
            db: Session = info.context["db"]
            all_words = [w.text for w in db.query(WordModel).all()]
            related_dict = analyzer.find_related_words(word, all_words)
            related_words = [w for sublist in related_dict.values() for w in sublist]
        
        return MorphemeAnalysis(
            word=word,
            morphemes=[
                Morpheme(
                    text=m.text,
                    type=m.type,
                    meaning=m.meaning
                ) for m in morphemes
            ],
            related_words=related_words
        )

    @strawberry.field
    def get_morpheme_statistics(
        self,
        info: Info,
        language_code: Optional[str] = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Get statistics about morpheme usage in the database.
        
        Args:
            language_code: Optional language code to filter words
            
        Returns:
            Dictionary of morpheme frequencies by type
        """
        db: Session = info.context["db"]
        query = db.query(WordModel)
        
        if language_code:
            query = query.join(LanguageModel).filter(
                LanguageModel.code == language_code
            )
        
        words = [w.text for w in query.all()]
        analyzer = MorphemeAnalyzer()
        
        return analyzer.get_morpheme_frequency(words)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_word(
        self,
        info: Info,
        text: str,
        language_id: int,
        pronunciation: Optional[str] = None,
        definition: Optional[str] = None,
    ) -> Word:
        db: Session = info.context["db"]
        word = WordModel(
            text=text,
            language_id=language_id,
            pronunciation=pronunciation,
            definition=definition,
        )
        db.add(word)
        db.commit()
        db.refresh(word)
        return word

    @strawberry.mutation
    def add_etymology(
        self,
        info: Info,
        word_id: int,
        ancestor_id: Optional[int],
        relationship_type: str,
        confidence_score: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Etymology:
        db: Session = info.context["db"]
        etymology = EtymologyModel(
            word_id=word_id,
            ancestor_id=ancestor_id,
            relationship_type=relationship_type,
            confidence_score=confidence_score,
            notes=notes,
        )
        db.add(etymology)
        db.commit()
        db.refresh(etymology)
        return etymology

    @strawberry.mutation
    def add_cognate_relationship(
        self,
        info: Info,
        word_id: int,
        cognate_id: int,
        confidence_score: Optional[int] = None,
    ) -> Word:
        db: Session = info.context["db"]
        word = db.query(WordModel).get(word_id)
        cognate = db.query(WordModel).get(cognate_id)
        if word and cognate:
            word.cognates.append(cognate)
            db.commit()
        return word

    @strawberry.mutation
    def add_cognate_relationship_with_detection(
        self,
        info: Info,
        word_id: int,
        candidate_word: str,
        min_confidence: float = 0.7
    ) -> Word:
        """
        Add a cognate relationship after automatic detection.
        
        Args:
            word_id: ID of the source word
            candidate_word: Text of the potential cognate
            min_confidence: Minimum confidence score for cognate detection
            
        Returns:
            Updated word with new cognate relationship if detected
        """
        db: Session = info.context["db"]
        word = db.query(WordModel).get(word_id)
        
        if not word:
            raise ValueError(f"Word with ID {word_id} not found")
        
        # Initialize cognate detector
        detector = CognateDetector(similarity_threshold=min_confidence)
        
        # Check if words are cognates
        score = detector.detect_cognates(word.text, candidate_word)
        
        if score.is_cognate:
            # Find or create the candidate word
            candidate = db.query(WordModel).filter(
                WordModel.text == candidate_word
            ).first()
            
            if candidate and candidate not in word.cognates:
                word.cognates.append(candidate)
                db.commit()
        
        return word 