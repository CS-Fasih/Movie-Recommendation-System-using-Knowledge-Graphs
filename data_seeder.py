"""
Movie Knowledge Graph Data Seeder
=================================

This script populates the Neo4j database with sample movie data.
It creates nodes (Movies, People, Genres) and relationships to demonstrate
the power of graph databases in recommendation systems.

Author: Senior Graph Database Engineer
Purpose: University Project - Initial Data Loading
"""

from db_connection import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSeeder:
    """
    Handles seeding of sample movie data into Neo4j.
    """
    
    def __init__(self):
        """Initialize the data seeder with database connection."""
        self.db = get_db_connection()
        if not self.db.connect():
            raise Exception("Failed to connect to Neo4j database")
    
    def clear_existing_data(self):
        """Clear all existing data from the database."""
        logger.info("🗑️  Clearing existing data...")
        if self.db.clear_database():
            logger.info("✓ Database cleared successfully")
        else:
            logger.error("✗ Failed to clear database")
    
    def create_constraints_and_indexes(self):
        """
        Create uniqueness constraints and indexes for better performance.
        Constraints ensure data integrity in the knowledge graph.
        """
        logger.info("📋 Creating constraints and indexes...")
        
        constraints = [
            # Ensure movie titles are unique
            "CREATE CONSTRAINT movie_title_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.title IS UNIQUE",
            # Ensure person names are unique
            "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
            # Ensure genre names are unique
            "CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE"
        ]
        
        for constraint in constraints:
            self.db.execute_write(constraint)
        
        # Create indexes for faster lookups
        self.db.create_indexes()
        logger.info("✓ Constraints and indexes created")
    
    def seed_genres(self):
        """
        Create Genre nodes in the knowledge graph.
        Genres are used to categorize movies and find similar content.
        """
        logger.info("🎭 Seeding genres...")
        
        genres = [
            {"name": "Action", "description": "High-energy films with physical stunts and chase sequences"},
            {"name": "Drama", "description": "Character-driven stories with emotional depth"},
            {"name": "Comedy", "description": "Light-hearted films designed to make audiences laugh"},
            {"name": "Sci-Fi", "description": "Science fiction exploring futuristic concepts"},
            {"name": "Thriller", "description": "Suspenseful films that keep viewers on edge"}
        ]
        
        # MERGE ensures we don't create duplicates (idempotent operation)
        query = """
        UNWIND $genres AS genre
        MERGE (g:Genre {name: genre.name})
        SET g.description = genre.description
        RETURN g.name as name
        """
        
        result = self.db.execute_query(query, {"genres": genres})
        logger.info(f"✓ Created {len(result)} genres")
    
    def seed_people(self):
        """
        Create Person nodes (Actors and Directors) in the knowledge graph.
        People can have multiple roles across different movies.
        """
        logger.info("👥 Seeding actors and directors...")
        
        people = [
            # Actors
            {"name": "Leonardo DiCaprio", "born": 1974, "role": "Actor"},
            {"name": "Tom Hanks", "born": 1956, "role": "Actor"},
            {"name": "Scarlett Johansson", "born": 1984, "role": "Actor"},
            {"name": "Morgan Freeman", "born": 1937, "role": "Actor"},
            {"name": "Keanu Reeves", "born": 1964, "role": "Actor"},
            {"name": "Christian Bale", "born": 1974, "role": "Actor"},
            {"name": "Matthew McConaughey", "born": 1969, "role": "Actor"},
            # Directors
            {"name": "Christopher Nolan", "born": 1970, "role": "Director"},
            {"name": "Quentin Tarantino", "born": 1963, "role": "Director"},
            {"name": "Steven Spielberg", "born": 1946, "role": "Director"},
        ]
        
        # MERGE prevents duplicate people if script is run multiple times
        query = """
        UNWIND $people AS person
        MERGE (p:Person {name: person.name})
        SET p.born = person.born,
            p.role = person.role
        RETURN p.name as name
        """
        
        result = self.db.execute_query(query, {"people": people})
        logger.info(f"✓ Created {len(result)} people (actors and directors)")
    
    def seed_movies(self):
        """
        Create Movie nodes with rich metadata.
        Each movie will be connected to genres, directors, and actors.
        """
        logger.info("🎬 Seeding movies...")
        
        movies = [
            {
                "title": "Inception",
                "year": 2010,
                "rating": 8.8,
                "tagline": "Your mind is the scene of the crime",
                "description": "A thief who steals corporate secrets through dream-sharing technology"
            },
            {
                "title": "The Dark Knight",
                "year": 2008,
                "rating": 9.0,
                "tagline": "Why so serious?",
                "description": "Batman faces the Joker in a battle for Gotham's soul"
            },
            {
                "title": "Interstellar",
                "year": 2014,
                "rating": 8.6,
                "tagline": "Mankind was born on Earth. It was never meant to die here.",
                "description": "A team of explorers travel through a wormhole in space"
            },
            {
                "title": "The Matrix",
                "year": 1999,
                "rating": 8.7,
                "tagline": "Welcome to the Real World",
                "description": "A computer hacker learns about the true nature of reality"
            },
            {
                "title": "Pulp Fiction",
                "year": 1994,
                "rating": 8.9,
                "tagline": "You won't know the facts until you've seen the fiction",
                "description": "Various interconnected stories of Los Angeles criminals"
            },
            {
                "title": "Forrest Gump",
                "year": 1994,
                "rating": 8.8,
                "tagline": "Life is like a box of chocolates",
                "description": "The story of a simple man with a big heart"
            },
            {
                "title": "The Shawshank Redemption",
                "year": 1994,
                "rating": 9.3,
                "tagline": "Fear can hold you prisoner. Hope can set you free.",
                "description": "Two imprisoned men bond over years, finding redemption"
            },
            {
                "title": "Saving Private Ryan",
                "year": 1998,
                "rating": 8.6,
                "tagline": "The mission is a man.",
                "description": "A group of soldiers search for a paratrooper during WWII"
            },
            {
                "title": "The Prestige",
                "year": 2006,
                "rating": 8.5,
                "tagline": "Are you watching closely?",
                "description": "Two magicians engage in a bitter rivalry"
            },
            {
                "title": "Memento",
                "year": 2000,
                "rating": 8.4,
                "tagline": "Some memories are best forgotten",
                "description": "A man with short-term memory loss attempts to track down his wife's murderer"
            }
        ]
        
        query = """
        UNWIND $movies AS movie
        MERGE (m:Movie {title: movie.title})
        SET m.year = movie.year,
            m.rating = movie.rating,
            m.tagline = movie.tagline,
            m.description = movie.description
        RETURN m.title as title
        """
        
        result = self.db.execute_query(query, {"movies": movies})
        logger.info(f"✓ Created {len(result)} movies")
    
    def create_relationships(self):
        """
        Create relationships between movies, people, and genres.
        This is where the POWER of graph databases shines!
        
        Relationships created:
        - DIRECTED: Person -> Movie (who directed which movie)
        - ACTED_IN: Person -> Movie (who acted in which movie)
        - IN_GENRE: Movie -> Genre (what genres each movie belongs to)
        """
        logger.info("🔗 Creating relationships...")
        
        # Director relationships
        # Cypher uses MATCH to find nodes, then CREATE/MERGE for relationships
        director_relationships = [
            ("Christopher Nolan", "Inception"),
            ("Christopher Nolan", "The Dark Knight"),
            ("Christopher Nolan", "Interstellar"),
            ("Christopher Nolan", "The Prestige"),
            ("Christopher Nolan", "Memento"),
            ("Quentin Tarantino", "Pulp Fiction"),
            ("Steven Spielberg", "Forrest Gump"),
            ("Steven Spielberg", "Saving Private Ryan"),
        ]
        
        query = """
        UNWIND $relationships AS rel
        MATCH (p:Person {name: rel.person})
        MATCH (m:Movie {title: rel.movie})
        MERGE (p)-[:DIRECTED]->(m)
        """
        
        relationships_data = [
            {"person": person, "movie": movie} 
            for person, movie in director_relationships
        ]
        self.db.execute_write(query, {"relationships": relationships_data})
        logger.info(f"✓ Created {len(director_relationships)} DIRECTED relationships")
        
        # Actor relationships
        # Note: One actor can act in multiple movies (many-to-many relationship)
        actor_relationships = [
            ("Leonardo DiCaprio", "Inception"),
            ("Leonardo DiCaprio", "The Prestige"),
            ("Tom Hanks", "Forrest Gump"),
            ("Tom Hanks", "Saving Private Ryan"),
            ("Scarlett Johansson", "The Prestige"),
            ("Morgan Freeman", "The Shawshank Redemption"),
            ("Keanu Reeves", "The Matrix"),
            ("Christian Bale", "The Dark Knight"),
            ("Christian Bale", "The Prestige"),
            ("Matthew McConaughey", "Interstellar"),
        ]
        
        query = """
        UNWIND $relationships AS rel
        MATCH (p:Person {name: rel.person})
        MATCH (m:Movie {title: rel.movie})
        MERGE (p)-[:ACTED_IN]->(m)
        """
        
        relationships_data = [
            {"person": person, "movie": movie} 
            for person, movie in actor_relationships
        ]
        self.db.execute_write(query, {"relationships": relationships_data})
        logger.info(f"✓ Created {len(actor_relationships)} ACTED_IN relationships")
        
        # Genre relationships
        # A movie can belong to multiple genres (important for recommendations!)
        genre_relationships = [
            ("Inception", "Sci-Fi"),
            ("Inception", "Action"),
            ("Inception", "Thriller"),
            ("The Dark Knight", "Action"),
            ("The Dark Knight", "Drama"),
            ("Interstellar", "Sci-Fi"),
            ("Interstellar", "Drama"),
            ("The Matrix", "Sci-Fi"),
            ("The Matrix", "Action"),
            ("Pulp Fiction", "Drama"),
            ("Pulp Fiction", "Thriller"),
            ("Forrest Gump", "Drama"),
            ("Forrest Gump", "Comedy"),
            ("The Shawshank Redemption", "Drama"),
            ("Saving Private Ryan", "Drama"),
            ("Saving Private Ryan", "Action"),
            ("The Prestige", "Drama"),
            ("The Prestige", "Thriller"),
            ("Memento", "Thriller"),
            ("Memento", "Drama"),
        ]
        
        query = """
        UNWIND $relationships AS rel
        MATCH (m:Movie {title: rel.movie})
        MATCH (g:Genre {name: rel.genre})
        MERGE (m)-[:IN_GENRE]->(g)
        """
        
        relationships_data = [
            {"movie": movie, "genre": genre} 
            for movie, genre in genre_relationships
        ]
        self.db.execute_write(query, {"relationships": relationships_data})
        logger.info(f"✓ Created {len(genre_relationships)} IN_GENRE relationships")
    
    def verify_data(self):
        """
        Verify that all data was seeded correctly.
        Runs several queries to count nodes and relationships.
        """
        logger.info("🔍 Verifying seeded data...")
        
        # Count nodes
        node_counts = {
            "Movies": "MATCH (m:Movie) RETURN count(m) as count",
            "People": "MATCH (p:Person) RETURN count(p) as count",
            "Genres": "MATCH (g:Genre) RETURN count(g) as count"
        }
        
        for label, query in node_counts.items():
            result = self.db.execute_query(query)
            count = result[0]['count'] if result else 0
            logger.info(f"  • {label}: {count}")
        
        # Count relationships
        rel_counts = {
            "DIRECTED": "MATCH ()-[r:DIRECTED]->() RETURN count(r) as count",
            "ACTED_IN": "MATCH ()-[r:ACTED_IN]->() RETURN count(r) as count",
            "IN_GENRE": "MATCH ()-[r:IN_GENRE]->() RETURN count(r) as count"
        }
        
        for rel_type, query in rel_counts.items():
            result = self.db.execute_query(query)
            count = result[0]['count'] if result else 0
            logger.info(f"  • {rel_type}: {count}")
    
    def seed_all(self, clear_first: bool = True):
        """
        Main method to seed all data into the database.
        
        Args:
            clear_first: If True, clears existing data before seeding
        """
        logger.info("=" * 60)
        logger.info("🌱 Starting Data Seeding Process")
        logger.info("=" * 60)
        
        try:
            if clear_first:
                self.clear_existing_data()
            
            # Create constraints first (ensures data integrity)
            self.create_constraints_and_indexes()
            
            # Create nodes
            self.seed_genres()
            self.seed_people()
            self.seed_movies()
            
            # Create relationships (the graph structure!)
            self.create_relationships()
            
            # Verify everything worked
            self.verify_data()
            
            logger.info("=" * 60)
            logger.info("✅ Data Seeding Complete!")
            logger.info("=" * 60)
            logger.info("Your knowledge graph is ready for recommendations!")
            
        except Exception as e:
            logger.error(f"❌ Error during seeding: {e}")
            raise


def main():
    """
    Main entry point for the data seeding script.
    """
    print("\n" + "=" * 60)
    print("🎬 Movie Knowledge Graph Data Seeder")
    print("=" * 60)
    print("\nThis script will populate your Neo4j database with sample")
    print("movie data including:")
    print("  • 10 Movies")
    print("  • 10 People (7 actors, 3 directors)")
    print("  • 5 Genres")
    print("  • Relationships connecting them all")
    print("\n" + "=" * 60)
    
    # Prompt user
    response = input("\n⚠️  This will CLEAR existing data. Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Seeding cancelled.")
        return
    
    try:
        seeder = DataSeeder()
        seeder.seed_all(clear_first=True)
        print("\n✅ Success! You can now run the Streamlit app:")
        print("   streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Failed to seed data: {e}")
        print("\nPlease check:")
        print("1. Neo4j is running and accessible")
        print("2. Your .env file has correct credentials")
        print("3. You have write permissions to the database")


if __name__ == "__main__":
    main()
