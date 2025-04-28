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
    etymologies = relationship("EtymologyModel", back_populates="word")
    cognates = relationship(
        "Word",
        secondary="cognate_relationship",
        primaryjoin="Word.id==cognate_relationship.c.word_id",
        secondaryjoin="Word.id==cognate_relationship.c.cognate_id",
    )


class EtymologyModel(Base):
    __tablename__ = 'etymologies'

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'))
    language = Column(String)
    meaning = Column(String)
    notes = Column(String)

    word = relationship("Word", back_populates="etymologies")


# Association table for cognate relationships
cognate_relationship = Table(
    "cognate_relationship",
    Base.metadata,
    Column("word_id", Integer, ForeignKey("word.id"), primary_key=True),
    Column("cognate_id", Integer, ForeignKey("word.id"), primary_key=True),
    Column("confidence_score", Integer),  # 0-100
) 