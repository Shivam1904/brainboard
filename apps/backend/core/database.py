from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLite engine
engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they are registered with Base
        from models.database import (
            Summary,
            User, DashboardWidget,
            TodoItem, WebSearchQuery, Alarm,
            SingleItemTracker, SingleItemTrackerLog,
            DailyWidget
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default user if not exists
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Check if default user exists
            existing_user = session.query(User).filter_by(email="default@brainboard.com").first()
            if not existing_user:
                default_user = User(
                    email="default@brainboard.com",
                    name="Default User"
                )
                session.add(default_user)
                session.commit()
                logger.info("Default user created successfully")
        except Exception as e:
            logger.warning(f"Could not create default user: {e}")
            session.rollback()
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def _create_default_user():
    """Create default user for development"""
    try:
        from models.database import User
        
        db = SessionLocal()
        # Check if default user exists
        existing_user = db.query(User).filter(User.email == "default@brainboard.com").first()
        
        if not existing_user:
            default_user = User(
                email="default@brainboard.com",
                name="Default User"
            )
            db.add(default_user)
            db.commit()
            logger.info("Default user created successfully")
        else:
            logger.info("Default user already exists")
            
        db.close()
    except Exception as e:
        logger.error(f"Failed to create default user: {e}")
