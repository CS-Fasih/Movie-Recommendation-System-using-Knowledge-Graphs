"""
Movie Recommendation Engine
===========================

This module contains the core recommendation logic using Cypher queries.
It demonstrates the power of graph databases for finding patterns and 
connections that would be complex in relational databases.

Author: Senior Graph Database Engineer
Purpose: University Project - Graph-Based Recommendations
"""

from typing import List, Dict, Any, Optional
from db_connection import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Handles movie recommendations using graph traversal algorithms.
    
    This class demonstrates how graph databases excel at finding
    relationships and patterns in connected data.
    """
    
    def __init__(self):
        """Initialize the recommendation engine with database connection."""
        self.db = get_db_connection()
        if not self.db.connect():
            raise Exception("Failed to connect to Neo4j database")
    
    def get_all_movies(self) -> List[Dict[str, Any]]:
        """
        Retrieve all movies from the database.
        
        Returns:
            List of dictionaries containing movie information
        """
        # Simple Cypher query to get all Movie nodes
        # ORDER BY ensures consistent ordering for UI dropdowns
        query = """
        MATCH (m:Movie)
        RETURN m.title as title, 
               m.year as year, 
               m.rating as rating,
               m.tagline as tagline,
               m.description as description
        ORDER BY m.title
        """
        
        return self.db.execute_query(query)
    
    def get_movie_details(self, movie_title: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive details for a specific movie including:
        - Basic movie information
        - Director(s)
        - Cast (actors)
        - Genres
        
        This demonstrates a graph traversal across multiple relationship types.
        
        Args:
            movie_title: Title of the movie to retrieve
            
        Returns:
            Dictionary with movie details or None if not found
        """
        # This Cypher query demonstrates OPTIONAL MATCH
        # OPTIONAL MATCH is like SQL's LEFT JOIN - returns null if no match
        # COLLECT aggregates multiple relationships into a list
        query = """
        MATCH (m:Movie {title: $title})
        
        // Find the director(s) - a movie can have multiple directors
        OPTIONAL MATCH (director:Person)-[:DIRECTED]->(m)
        
        // Find all actors in this movie
        OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(m)
        
        // Find all genres this movie belongs to
        OPTIONAL MATCH (m)-[:IN_GENRE]->(genre:Genre)
        
        // COLLECT aggregates results into lists
        // This is powerful: one query returns everything!
        RETURN m.title as title,
               m.year as year,
               m.rating as rating,
               m.tagline as tagline,
               m.description as description,
               COLLECT(DISTINCT director.name) as directors,
               COLLECT(DISTINCT actor.name) as cast,
               COLLECT(DISTINCT genre.name) as genres
        """
        
        result = self.db.execute_query(query, {"title": movie_title})
        
        if not result:
            logger.warning(f"Movie '{movie_title}' not found")
            return None
        
        return result[0]
    
    def get_similar_movies_by_genre(self, movie_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find movies similar to the given movie based on SHARED GENRES.
        
        This is a classic graph database use case:
        "Find movies that share genres with this movie, but aren't this movie"
        
        In a relational database, this would require multiple JOINs.
        In a graph database, it's a simple pattern match!
        
        Args:
            movie_title: Reference movie title
            limit: Maximum number of recommendations
            
        Returns:
            List of similar movies with shared genre count
        """
        # This Cypher query demonstrates:
        # 1. Pattern matching across multiple hops
        # 2. Filtering (WHERE clause)
        # 3. Aggregation (COUNT)
        # 4. Ordering by relevance
        query = """
        // Start with the selected movie
        MATCH (selected:Movie {title: $title})
        
        // Find genres of the selected movie
        MATCH (selected)-[:IN_GENRE]->(g:Genre)
        
        // Find OTHER movies that share these genres
        // The pattern: selected -> genre <- other_movies
        MATCH (other:Movie)-[:IN_GENRE]->(g)
        
        // Don't recommend the same movie!
        WHERE other <> selected
        
        // Count how many genres are shared (more = more similar)
        WITH other, COUNT(DISTINCT g) as shared_genres
        
        // Get additional movie details
        MATCH (other)
        OPTIONAL MATCH (other)-[:IN_GENRE]->(genre:Genre)
        
        // Return results ordered by similarity
        RETURN other.title as title,
               other.year as year,
               other.rating as rating,
               other.tagline as tagline,
               shared_genres,
               COLLECT(DISTINCT genre.name) as genres
        ORDER BY shared_genres DESC, other.rating DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {"title": movie_title, "limit": limit})
    
    def get_similar_movies_by_cast(self, movie_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find movies similar to the given movie based on SHARED ACTORS.
        
        Logic: "If you liked a movie with actor X, you might like other 
        movies with actor X"
        
        Args:
            movie_title: Reference movie title
            limit: Maximum number of recommendations
            
        Returns:
            List of similar movies with shared actor count
        """
        # Similar pattern to genre-based, but using ACTED_IN relationships
        query = """
        // Start with the selected movie
        MATCH (selected:Movie {title: $title})
        
        // Find actors in the selected movie
        MATCH (actor:Person)-[:ACTED_IN]->(selected)
        
        // Find OTHER movies these actors appear in
        MATCH (actor)-[:ACTED_IN]->(other:Movie)
        
        // Don't recommend the same movie
        WHERE other <> selected
        
        // Count shared actors
        WITH other, COUNT(DISTINCT actor) as shared_actors,
             COLLECT(DISTINCT actor.name) as common_actors
        
        // Get movie details
        MATCH (other)
        OPTIONAL MATCH (other)-[:IN_GENRE]->(genre:Genre)
        
        RETURN other.title as title,
               other.year as year,
               other.rating as rating,
               other.tagline as tagline,
               shared_actors,
               common_actors,
               COLLECT(DISTINCT genre.name) as genres
        ORDER BY shared_actors DESC, other.rating DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {"title": movie_title, "limit": limit})
    
    def get_combined_recommendations(self, movie_title: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Get recommendations based on BOTH genres AND cast.
        
        This is the MOST POWERFUL recommendation approach:
        - Finds movies with shared genres OR shared actors
        - Ranks by TOTAL similarity score
        - Gives bonus points for having both
        
        This demonstrates the true power of graph databases!
        
        Args:
            movie_title: Reference movie title
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended movies with similarity scores
        """
        # This advanced query combines multiple patterns
        # and calculates a similarity score
        query = """
        // Start with the selected movie
        MATCH (selected:Movie {title: $title})
        
        // Find all other movies
        MATCH (other:Movie)
        WHERE other <> selected
        
        // Count shared genres
        OPTIONAL MATCH (selected)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(other)
        WITH selected, other, COUNT(DISTINCT g) as genre_score
        
        // Count shared actors
        OPTIONAL MATCH (selected)<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(other)
        WITH selected, other, genre_score, COUNT(DISTINCT a) as actor_score
        
        // Only include movies with at least one shared attribute
        WHERE genre_score > 0 OR actor_score > 0
        
        // Calculate combined similarity score
        // Genres get 2x weight, actors get 3x weight
        WITH other,
             genre_score as total_genre_score,
             actor_score as total_actor_score,
             (genre_score * 2 + actor_score * 3) as similarity_score
        
        // Get full movie details
        OPTIONAL MATCH (other)-[:IN_GENRE]->(genre:Genre)
        OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(other)
        OPTIONAL MATCH (director:Person)-[:DIRECTED]->(other)
        
        RETURN other.title as title,
               other.year as year,
               other.rating as rating,
               other.tagline as tagline,
               other.description as description,
               total_genre_score as shared_genres,
               total_actor_score as shared_actors,
               similarity_score,
               COLLECT(DISTINCT genre.name) as genres,
               COLLECT(DISTINCT actor.name) as cast,
               COLLECT(DISTINCT director.name) as directors
        ORDER BY similarity_score DESC, other.rating DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {"title": movie_title, "limit": limit})
    
    def get_movies_by_director(self, director_name: str) -> List[Dict[str, Any]]:
        """
        Find all movies directed by a specific person.
        
        Args:
            director_name: Name of the director
            
        Returns:
            List of movies directed by this person
        """
        query = """
        MATCH (director:Person {name: $name})-[:DIRECTED]->(movie:Movie)
        OPTIONAL MATCH (movie)-[:IN_GENRE]->(genre:Genre)
        RETURN movie.title as title,
               movie.year as year,
               movie.rating as rating,
               COLLECT(DISTINCT genre.name) as genres
        ORDER BY movie.year DESC
        """
        
        return self.db.execute_query(query, {"name": director_name})
    
    def get_movies_by_actor(self, actor_name: str) -> List[Dict[str, Any]]:
        """
        Find all movies featuring a specific actor.
        
        Args:
            actor_name: Name of the actor
            
        Returns:
            List of movies featuring this actor
        """
        query = """
        MATCH (actor:Person {name: $name})-[:ACTED_IN]->(movie:Movie)
        OPTIONAL MATCH (movie)-[:IN_GENRE]->(genre:Genre)
        RETURN movie.title as title,
               movie.year as year,
               movie.rating as rating,
               COLLECT(DISTINCT genre.name) as genres
        ORDER BY movie.year DESC
        """
        
        return self.db.execute_query(query, {"name": actor_name})
    
    def get_graph_visualization_data(self, movie_title: str) -> Dict[str, Any]:
        """
        Get data for visualizing the knowledge graph around a movie.
        
        Returns nodes and edges for graph visualization in Streamlit.
        
        Args:
            movie_title: Title of the movie to visualize
            
        Returns:
            Dictionary with 'nodes' and 'edges' for visualization
        """
        query = """
        // Get the movie and all its immediate connections
        MATCH (m:Movie {title: $title})
        OPTIONAL MATCH (director:Person)-[:DIRECTED]->(m)
        OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(m)
        OPTIONAL MATCH (m)-[:IN_GENRE]->(genre:Genre)
        
        // Return all nodes and relationships
        RETURN m, 
               COLLECT(DISTINCT director) as directors,
               COLLECT(DISTINCT actor) as actors,
               COLLECT(DISTINCT genre) as genres
        """
        
        result = self.db.execute_query(query, {"title": movie_title})
        
        if not result:
            return {"nodes": [], "edges": []}
        
        data = result[0]
        nodes = []
        edges = []
        
        # Add movie node
        movie_node = {
            "id": movie_title,
            "label": movie_title,
            "type": "movie",
            "size": 30,
            "color": "#FF6B6B"
        }
        nodes.append(movie_node)
        
        # Add director nodes and edges
        for director in data.get('directors', []):
            if director:  # Check if not None
                director_name = director.get('name', 'Unknown')
                nodes.append({
                    "id": f"dir_{director_name}",
                    "label": director_name,
                    "type": "director",
                    "size": 20,
                    "color": "#4ECDC4"
                })
                edges.append({
                    "source": f"dir_{director_name}",
                    "target": movie_title,
                    "label": "DIRECTED",
                    "color": "#95E1D3"
                })
        
        # Add actor nodes and edges
        for actor in data.get('actors', []):
            if actor:
                actor_name = actor.get('name', 'Unknown')
                nodes.append({
                    "id": f"act_{actor_name}",
                    "label": actor_name,
                    "type": "actor",
                    "size": 20,
                    "color": "#A8E6CF"
                })
                edges.append({
                    "source": f"act_{actor_name}",
                    "target": movie_title,
                    "label": "ACTED_IN",
                    "color": "#DCEDC1"
                })
        
        # Add genre nodes and edges
        for genre in data.get('genres', []):
            if genre:
                genre_name = genre.get('name', 'Unknown')
                nodes.append({
                    "id": f"gen_{genre_name}",
                    "label": genre_name,
                    "type": "genre",
                    "size": 15,
                    "color": "#FFD93D"
                })
                edges.append({
                    "source": movie_title,
                    "target": f"gen_{genre_name}",
                    "label": "IN_GENRE",
                    "color": "#FFF9E6"
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get database statistics for dashboard display.
        
        Returns:
            Dictionary with counts of movies, people, genres, and relationships
        """
        stats = {}
        
        # Count nodes
        queries = {
            "total_movies": "MATCH (m:Movie) RETURN count(m) as count",
            "total_people": "MATCH (p:Person) RETURN count(p) as count",
            "total_genres": "MATCH (g:Genre) RETURN count(g) as count",
            "total_relationships": "MATCH ()-[r]->() RETURN count(r) as count"
        }
        
        for key, query in queries.items():
            result = self.db.execute_query(query)
            stats[key] = result[0]['count'] if result else 0
        
        return stats


def test_recommendations():
    """
    Test function to verify recommendation engine works correctly.
    """
    print("\n" + "=" * 60)
    print("🧪 Testing Recommendation Engine")
    print("=" * 60)
    
    try:
        engine = RecommendationEngine()
        
        # Test 1: Get all movies
        print("\n1. Getting all movies...")
        movies = engine.get_all_movies()
        print(f"   ✓ Found {len(movies)} movies")
        
        # Test 2: Get movie details
        print("\n2. Getting details for 'Inception'...")
        details = engine.get_movie_details("Inception")
        if details:
            print(f"   ✓ Title: {details['title']}")
            print(f"   ✓ Directors: {', '.join(details['directors'])}")
            print(f"   ✓ Cast: {', '.join(details['cast'][:3])}...")
            print(f"   ✓ Genres: {', '.join(details['genres'])}")
        
        # Test 3: Get recommendations
        print("\n3. Getting recommendations for 'Inception'...")
        recommendations = engine.get_combined_recommendations("Inception", limit=5)
        print(f"   ✓ Found {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"      {i}. {rec['title']} (Score: {rec['similarity_score']})")
        
        # Test 4: Get statistics
        print("\n4. Getting database statistics...")
        stats = engine.get_statistics()
        print(f"   ✓ Movies: {stats['total_movies']}")
        print(f"   ✓ People: {stats['total_people']}")
        print(f"   ✓ Genres: {stats['total_genres']}")
        print(f"   ✓ Relationships: {stats['total_relationships']}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Recommendation engine is working.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_recommendations()
