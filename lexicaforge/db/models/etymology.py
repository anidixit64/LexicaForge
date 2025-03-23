from sqlalchemy import Column, String, Integer, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base


class LanguageFamily(enum.Enum):
    INDO_EUROPEAN = "Indo-European"
    SINO_TIBETAN = "Sino-Tibetan"
    AFROASIATIC = "Afroasiatic"
    AUSTRONESIAN = "Austronesian"
    DRAVIDIAN = "Dravidian"
    OTHER = "Other"


class Language(Base):
    """Model for language information."""
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    family = Column(Enum(LanguageFamily), nullable=False)
    
    words = relationship("Word", back_populates="language")


class Word(Base):
    """Model for word entries."""
    text = Column(String(100), nullable=False)
    language_id = Column(Integer, ForeignKey("language.id"), nullable=False)
    pronunciation = Column(String(100))
    definition = Column(String(500))
    
    language = relationship("Language", back_populates="words")
    etymologies = relationship("Etymology", back_populates="word")
    cognates = relationship(
        "Word",
        secondary="cognate_relationship",
        primaryjoin="Word.id==cognate_relationship.c.word_id",
        secondaryjoin="Word.id==cognate_relationship.c.cognate_id",
    )


class Etymology(Base):
    """Model for etymological relationships."""
    word_id = Column(Integer, ForeignKey("word.id"), nullable=False)
    ancestor_id = Column(Integer, ForeignKey("word.id"), nullable=True)
    relationship_type = Column(String(50), nullable=False)  # e.g., "derived", "borrowed", "inherited"
    confidence_score = Column(Integer)  # 0-100
    notes = Column(String(500))
    
    word = relationship("Word", back_populates="etymologies", foreign_keys=[word_id])
    ancestor = relationship("Word", foreign_keys=[ancestor_id])


# Association table for cognate relationships
cognate_relationship = Table(
    "cognate_relationship",
    Base.metadata,
    Column("word_id", Integer, ForeignKey("word.id"), primary_key=True),
    Column("cognate_id", Integer, ForeignKey("word.id"), primary_key=True),
    Column("confidence_score", Integer),  # 0-100
) 