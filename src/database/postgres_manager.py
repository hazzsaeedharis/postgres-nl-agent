"""
PostgreSQL database manager for handling connections and queries
"""

import logging
import asyncio
from typing import Any, List, Dict, Optional
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.utils.config import Config

logger = logging.getLogger(__name__)

class PostgresManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        self.config = Config()
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self._connected = False
        
    async def connect(self):
        """Establish database connection"""
        try:
            database_url = self.config.get_database_url()
            
            # Create async engine
            self.async_engine = create_async_engine(
                database_url.replace("postgresql://", "postgresql+asyncpg://"),
                echo=self.config.debug,
                pool_size=10,
                max_overflow=20
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self._connected = True
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self._connected = False
            raise
    
    async def disconnect(self):
        """Close database connection"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            self._connected = False
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    async def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected
    
    async def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        if not self._connected:
            raise Exception("Database not connected")
        
        try:
            async with self.session_factory() as session:
                result = await session.execute(text(sql_query))
                
                if result.returns_rows:
                    # Fetch results for SELECT queries
                    rows = result.fetchall()
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    # For INSERT, UPDATE, DELETE queries
                    await session.commit()
                    return [{"affected_rows": result.rowcount}]
                    
        except Exception as e:
            logger.error(f"Error executing query '{sql_query}': {e}")
            raise
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table"""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
        """
        
        try:
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text(query), {"table_name": table_name})
                return [dict(row) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {e}")
            return []
    
    async def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        
        try:
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text(query))
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False 