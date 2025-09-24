"""
PostgreSQL database connection and operations using SQLAlchemy
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from utils.logger import Logger
from config.configures import config

# Import our models
from .models import Base, Book, Order, OrderStatus

logger = Logger(__name__).get_logger()

class PostgresDB:
    """PostgreSQL database manager using SQLAlchemy"""
    
    def __init__(self, host: str = None, port: int = None, user: str = None, 
                 password: str = None, dbname: str = None, database_url: str = None):
        """
        Initialize PostgreSQL connection
        Can use individual parameters, database_url, or configuration defaults
        """
        if database_url:
            self.database_url = database_url
        else:
            # Use provided parameters or fallback to configuration
            db_config = config.database
            self.host = host or db_config.host
            self.port = port or db_config.port
            self.user = user or db_config.user
            self.password = password or db_config.password
            self.dbname = dbname or db_config.name
            
            self.database_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        logger.debug(f"Database URL: {self.database_url}")
        self.engine = None
        self.SessionLocal = None
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Set to True for SQL debugging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            logger.info("Database connection established successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create all tables defined in models"""
        try:
            if not self.engine:
                self.connect()
                
            Base.metadata.create_all(bind=self.engine)
            logger.info("All tables created successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        try:
            if not self.engine:
                self.connect()
                
            Base.metadata.drop_all(bind=self.engine)
            logger.info("All tables dropped successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with automatic cleanup"""
        if not self.SessionLocal:
            self.connect()
            
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Execute raw SQL query"""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                if result.returns_rows:
                    return [dict(row._mapping) for row in result.fetchall()]
                return []
                
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if database is accessible"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
    
    @classmethod
    def from_config(cls) -> 'PostgresDB':
        """
        Create PostgresDB instance using the global configuration
        
        Returns:
            PostgresDB instance configured with settings from config
        """
        return cls(
            host=config.database.host,
            port=config.database.port,
            user=config.database.user,
            password=config.database.password,
            dbname=config.database.name
        )    