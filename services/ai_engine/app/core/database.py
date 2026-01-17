
import os
from dotenv import load_dotenv
load_dotenv()
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

class DatabaseManager:
    _instance = None
    _engine = None
    _SessionLocal = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the database connection using the Singleton pattern.
        Targeting: Google Cloud SQL (PostgreSQL).
        """
        # Connection configuration
        # In a real Cloud Run environment, these would be populated specifically for the Cloud SQL connector.
        # For now, we use the DATABASE_URL provided in .env which should point to the instance.
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Fallback/Default for Maelstrom DB
            # Note: This expects the proxy or direct connection to be available
            db_user = os.getenv("DB_USER", "postgres")
            db_pass = os.getenv("DB_PASS", "turboplanx_secure_password")
            db_name = os.getenv("DB_NAME", "turboplanx")
            db_host = os.getenv("DB_HOST", "localhost")
            database_url = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"

        print(f"⚡ [CASH MAELSTROM] Initializing Quantum Database Uplink...")
        
        self._engine = sqlalchemy.create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True, # Critical for cloud connections to handle disconnects
            connect_args={"connect_timeout": 5}
        )
        
        self._SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self._engine))
        print(f"✅ [CASH MAELSTROM] Database Singleton Active.")

    def get_session(self):
        """Returns a thread-safe database session."""
        return self._SessionLocal()

    def get_engine(self):
        return self._engine

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = DatabaseManager().get_session()
    try:
        yield db
    finally:
        db.close()
