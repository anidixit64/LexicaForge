import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from lexicaforge.db.config import SessionLocal
from lexicaforge.db.models.base import Base
from lexicaforge.db.models.etymology import Language, Word, Etymology, LanguageFamily
from lexicaforge.db.config import engine

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Add sample languages
        english = Language(name="English", code="en", family=LanguageFamily.INDO_EUROPEAN)
        german = Language(name="German", code="de", family=LanguageFamily.INDO_EUROPEAN)
        french = Language(name="French", code="fr", family=LanguageFamily.INDO_EUROPEAN)
        
        db.add_all([english, german, french])
        db.commit()
        
        # Add sample words with etymologies
        water = Word(
            text="water",
            language_id=english.id,
            pronunciation="ˈwɔːtə",
            definition="A clear, colorless liquid essential for life"
        )
        
        wasser = Word(
            text="Wasser",
            language_id=german.id,
            pronunciation="ˈvasɐ",
            definition="Wasser; Flüssigkeit, die als Regen vom Himmel fällt"
        )
        
        eau = Word(
            text="eau",
            language_id=french.id,
            pronunciation="o",
            definition="Liquide transparent, inodore et incolore"
        )
        
        db.add_all([water, wasser, eau])
        db.commit()
        
        # Add etymological relationships
        water_etymology = Etymology(
            word_id=water.id,
            relationship_type="inherited",
            notes="From Old English 'wæter', from Proto-Germanic *watōr",
            confidence_score=95
        )
        
        wasser_etymology = Etymology(
            word_id=wasser.id,
            relationship_type="inherited",
            notes="From Old High German 'wazzar', from Proto-Germanic *watōr",
            confidence_score=95
        )
        
        eau_etymology = Etymology(
            word_id=eau.id,
            relationship_type="inherited",
            notes="From Old French 'ewe', from Latin 'aqua'",
            confidence_score=95
        )
        
        db.add_all([water_etymology, wasser_etymology, eau_etymology])
        
        # Add cognate relationships
        water.cognates.append(wasser)
        wasser.cognates.append(water)
        
        db.commit()
        
        print("Database initialized with sample data!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 