"""
Neo4j Database Connection Manager
=================================

This module handles all interactions with the Neo4j graph database.
It provides a singleton connection manager to ensure efficient resource usage.

Author: Senior Graph Database Engineer
Purpose: University Project - Movie Recommendation System
"""

import os
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jConnection:
    """
    Singleton class to manage Neo4j database connections.
    
    This class ensures that only one database connection is maintained
    throughout the application lifecycle, improving performance and
    resource management.
    """
    
    _instance: Optional['Neo4jConnection'] = None
    _driver: Optional[Driver] = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the connection manager."""
        if not hasattr(self, 'initialized'):
            # Load environment variables from .env file
            load_dotenv()
            self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
            self.username = os.getenv('NEO4J_USERNAME', 'neo4j')
            self.password = os.getenv('NEO4J_PASSWORD', '')
            self.initialized = True
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self._driver is None:
                logger.info(f"Connecting to Neo4j at {self.uri}...")
                self._driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password),
                    max_connection_lifetime=3600,  # 1 hour
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=120
                )
                # Verify connectivity
                self._driver.verify_connectivity()
                logger.info("✓ Successfully connected to Neo4j database")
                return True
        except AuthError as e:
            logger.error(f"✗ Authentication failed: {e}")
            logger.error("Please check your NEO4J_USERNAME and NEO4J_PASSWORD in .env file")
            return False
        except ServiceUnavailable as e:
            logger.error(f"✗ Neo4j service unavailable: {e}")
            logger.error("Please ensure Neo4j is running and NEO4J_URI is correct")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error connecting to Neo4j: {e}")
            return False
    
    def close(self):
        """Close the database connection and cleanup resources."""
        if self._driver is not None:
            logger.info("Closing Neo4j connection...")
            self._driver.close()
            self._driver = None
            logger.info("✓ Connection closed")
    
    def get_session(self) -> Optional[Session]:
        """
        Get a database session for executing queries.
        
        Returns:
            Session: Neo4j session object or None if connection failed
        """
        if self._driver is None:
            if not self.connect():
                return None
        return self._driver.session()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Dictionary of query parameters
            
        Returns:
            List of dictionaries containing query results
        """
        parameters = parameters or {}
        session = self.get_session()
        
        if session is None:
            logger.error("Cannot execute query: No database session available")
            return []
        
        try:
            result = session.run(query, parameters)
            # Convert result to list of dictionaries
            records = [dict(record) for record in result]
            logger.info(f"✓ Query executed successfully, returned {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"✗ Error executing query: {e}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Parameters: {parameters}")
            return []
        finally:
            session.close()
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute a write transaction (CREATE, MERGE, DELETE, etc.).
        
        Args:
            query: Cypher query string
            parameters: Dictionary of query parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        parameters = parameters or {}
        session = self.get_session()
        
        if session is None:
            logger.error("Cannot execute write: No database session available")
            return False
        
        try:
            with session.begin_transaction() as tx:
                tx.run(query, parameters)
                tx.commit()
            logger.info("✓ Write transaction completed successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Error executing write transaction: {e}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Parameters: {parameters}")
            return False
        finally:
            session.close()
    
    def clear_database(self) -> bool:
        """
        Clear all nodes and relationships from the database.
        WARNING: This will delete all data!
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.warning("⚠️  Clearing database - all data will be deleted!")
        query = "MATCH (n) DETACH DELETE n"
        return self.execute_write(query)
    
    def create_indexes(self) -> bool:
        """
        Create database indexes for better query performance.
        
        Indexes are created on:
        - Movie.title
        - Person.name
        - Genre.name
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Creating database indexes for optimized queries...")
        
        indexes = [
            "CREATE INDEX movie_title_index IF NOT EXISTS FOR (m:Movie) ON (m.title)",
            "CREATE INDEX person_name_index IF NOT EXISTS FOR (p:Person) ON (p.name)",
            "CREATE INDEX genre_name_index IF NOT EXISTS FOR (g:Genre) ON (g.name)"
        ]
        
        success = True
        for index_query in indexes:
            if not self.execute_write(index_query):
                success = False
        
        if success:
            logger.info("✓ All indexes created successfully")
        else:
            logger.warning("⚠️  Some indexes failed to create")
        
        return success
    
    def verify_connection(self) -> bool:
        """
        Verify that the database connection is active and working.
        
        Returns:
            bool: True if connection is active, False otherwise
        """
        try:
            result = self.execute_query("RETURN 1 as test")
            return len(result) > 0 and result[0].get('test') == 1
        except Exception as e:
            logger.error(f"✗ Connection verification failed: {e}")
            return False


# Convenience function for getting database connection
def get_db_connection() -> Neo4jConnection:
    """
    Get the singleton Neo4j connection instance.
    
    Returns:
        Neo4jConnection: The database connection manager
    """
    return Neo4jConnection()


if __name__ == "__main__":
    """
    Test the database connection when running this module directly.
    """
    print("=" * 60)
    print("Neo4j Connection Manager - Test Mode")
    print("=" * 60)
    
    db = get_db_connection()
    
    if db.connect():
        print("\n✓ Connection test passed!")
        
        if db.verify_connection():
            print("✓ Connection verification passed!")
        else:
            print("✗ Connection verification failed!")
        
        db.close()
    else:
        print("\n✗ Connection test failed!")
        print("\nPlease check:")
        print("1. Neo4j is running (local) or accessible (cloud)")
        print("2. .env file exists with correct credentials")
        print("3. NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD are set correctly")
