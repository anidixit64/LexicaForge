import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from lexicaforge.api.main import app
from lexicaforge.db.models.base import Base
from lexicaforge.db.models.etymology import Language, LanguageFamily

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to LexicaForge API",
        "docs": "/docs",
        "graphql": "/graphql"
    }

def test_graphql_languages_query():
    # Add test data
    db = TestingSessionLocal()
    language = Language(
        name="English",
        code="en",
        family=LanguageFamily.INDO_EUROPEAN
    )
    db.add(language)
    db.commit()

    # GraphQL query
    query = """
    query {
        languages {
            name
            code
            family
        }
    }
    """
    
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert len(data["data"]["languages"]) == 1
    assert data["data"]["languages"][0]["name"] == "English"
    assert data["data"]["languages"][0]["code"] == "en"
    assert data["data"]["languages"][0]["family"] == "INDO_EUROPEAN" 