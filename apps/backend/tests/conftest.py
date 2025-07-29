import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from core.database import Base

@pytest.fixture(scope="function")
def temp_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    os.close(db_fd)
    os.remove(db_path)

# Add more fixtures for test client and test data as needed
