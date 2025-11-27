from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# --- 1. INITIALIZE GLOBAL ENGINE/URL ---
SQLALCHEMY_DATABASE_URL = None
engine = None
Base = declarative_base()

# --- 2. THE SAFE ENGINE CREATOR (Final ArgumentError Fix) ---
def get_engine():
    """Returns the engine, creating it if it doesn't exist."""
    global engine
    global SQLALCHEMY_DATABASE_URL

    if engine is None:
        # CRITICAL: Read the URL only when the function is executed
        SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
        
        # Check for URL string explicitly. This must be a string or it crashes.
        if not isinstance(SQLALCHEMY_DATABASE_URL, str) or not SQLALCHEMY_DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is MISSING. Please link 'culina-db' to 'Culina-AI' in Render.")

        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        
    return engine

# --- 3. THE DATABASE SESSION DEPENDENCY ---
def get_db():
    local_engine = get_engine()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=local_engine)
    db = SessionLocal()
    
    try:
        Base.metadata.create_all(bind=local_engine) 
        yield db
    finally:
        db.close()