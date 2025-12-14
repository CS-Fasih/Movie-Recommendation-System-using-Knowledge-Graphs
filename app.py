"""
Movie Recommendation System - Streamlit UI
=========================================

Interactive web application for movie recommendations using Neo4j knowledge graph.
This demonstrates the power of graph databases for connected data.

Author: Senior Graph Database Engineer
Purpose: University Project - Interactive Demo
"""

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from recommendation_engine import RecommendationEngine
from db_connection import get_db_connection
import logging
import os

# Configure page
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main theme colors */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #4ECDC4;
        margin-bottom: 2rem;
    }
    
    /* Movie details card - dark theme with good contrast */
    .movie-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #FF6B6B;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    .movie-card h2 {
        color: #FFD93D !important;
        margin-bottom: 0.5rem;
    }
    .movie-card p {
        color: #E8F5E9 !important;
        line-height: 1.6;
    }
    .movie-card strong {
        color: #FFD93D !important;
    }
    
    /* Recommendation cards - vibrant and readable */
    .recommendation-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #4ECDC4;
        margin-bottom: 1rem;
        box-shadow: 0 3px 5px rgba(0,0,0,0.2);
        color: white;
        transition: transform 0.2s;
    }
    .recommendation-card:hover {
        transform: translateX(5px);
    }
    .recommendation-card h4 {
        color: #FFD93D !important;
        margin-bottom: 0.8rem;
    }
    .recommendation-card p {
        color: #E8F5E9 !important;
        margin: 0.5rem 0;
    }
    .recommendation-card strong {
        color: #4ECDC4 !important;
    }
    
    /* Stat boxes */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stat-number {
        font-size: 3rem;
        font-weight: bold;
        color: #FFD93D;
    }
    .stat-label {
        font-size: 1.1rem;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    .info-box strong {
        color: #FFD93D !important;
    }
    
    /* Section headers */
    h3 {
        color: #4ECDC4 !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4ECDC4;
    }
    
    /* Improve overall text contrast */
    .stMarkdown {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_recommendation_engine():
    """
    Initialize and cache the recommendation engine.
    Caching prevents reconnecting to database on every interaction.
    """
    try:
        return RecommendationEngine()
    except Exception as e:
        logger.error(f"Failed to initialize recommendation engine: {e}")
        return None


def display_header():
    """Display the application header."""
    st.markdown('<div class="main-header">🎬 Smart Movie Recommendation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by Neo4j Knowledge Graph</div>', unsafe_allow_html=True)
    st.markdown("---")


def display_sidebar_stats(engine: RecommendationEngine):
    """
    Display database statistics in the sidebar.
    
    Args:
        engine: RecommendationEngine instance
    """
    st.sidebar.title("📊 Database Statistics")
    
    try:
        stats = engine.get_statistics()
        
        st.sidebar.metric("🎬 Total Movies", stats['total_movies'])
        st.sidebar.metric("👥 Total People", stats['total_people'])
        st.sidebar.metric("🎭 Total Genres", stats['total_genres'])
        st.sidebar.metric("🔗 Total Relationships", stats['total_relationships'])
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎓 About This Project")
        st.sidebar.info(
            "This system demonstrates the power of **Graph Databases** "
            "over traditional relational databases for recommendation systems.\n\n"
            "**Key Advantages:**\n"
            "- Natural representation of relationships\n"
            "- Fast pattern matching\n"
            "- Flexible schema\n"
            "- Powerful traversal queries"
        )
        
    except Exception as e:
        st.sidebar.error(f"Error loading stats: {e}")


def display_movie_details(movie_details: dict):
    """
    Display detailed information about a selected movie.
    
    Args:
        movie_details: Dictionary containing movie information
    """
    st.markdown("### 🎬 Movie Details")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="movie-card">
            <h2>{movie_details['title']} ({movie_details['year']})</h2>
            <p style="font-style: italic; color: #FFD93D; font-size: 1.1rem; margin: 1rem 0;">"{movie_details['tagline']}"</p>
            <p style="font-size: 1.05rem; line-height: 1.8;">{movie_details['description']}</p>
            <p style="font-size: 1.2rem; margin-top: 1rem;"><strong>⭐ Rating:</strong> <span style="color: #FFD93D;">{movie_details['rating']}/10</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Display director(s)
        st.markdown("""
        <div class="info-box">
            <p style="margin: 0;"><strong>🎬 Director(s):</strong></p>
        """, unsafe_allow_html=True)
        for director in movie_details['directors']:
            if director:  # Check for non-empty
                st.markdown(f"<p style='margin: 0.3rem 0; padding-left: 1rem; color: white;'>• {director}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display genres
        st.markdown("""
        <div class="info-box" style="margin-top: 1rem;">
            <p style="margin: 0;"><strong>🎭 Genres:</strong></p>
        """, unsafe_allow_html=True)
        for genre in movie_details['genres']:
            if genre:
                st.markdown(f"<p style='margin: 0.3rem 0; padding-left: 1rem; color: white;'>• {genre}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display cast
    st.markdown("""
    <div class="info-box">
        <p style="margin-bottom: 0.5rem;"><strong>👥 Cast:</strong></p>
    """, unsafe_allow_html=True)
    cast_text = ", ".join([actor for actor in movie_details['cast'] if actor])
    st.markdown(f"<p style='margin: 0; color: white; font-size: 1.05rem;'>{cast_text}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def display_recommendations(recommendations: list, rec_type: str = "Combined"):
    """
    Display recommended movies in a nice format.
    
    Args:
        recommendations: List of recommended movie dictionaries
        rec_type: Type of recommendation (for display purposes)
    """
    if not recommendations:
        st.warning("No recommendations found. Try selecting a different movie.")
        return
    
    st.markdown(f"### 🎯 Recommended Movies ({rec_type})")
    st.markdown(f"<p style='color: #4ECDC4; font-size: 1.1rem; margin-bottom: 1.5rem;'>Found {len(recommendations)} similar movies based on shared genres and cast</p>", unsafe_allow_html=True)
    
    for i, rec in enumerate(recommendations, 1):
        # Prepare similarity info
        similarity_info = []
        if 'shared_genres' in rec and rec['shared_genres'] > 0:
            similarity_info.append(f"{rec['shared_genres']} shared genre(s)")
        if 'shared_actors' in rec and rec['shared_actors'] > 0:
            similarity_info.append(f"{rec['shared_actors']} shared actor(s)")
        if 'similarity_score' in rec:
            similarity_info.append(f"Score: {rec['similarity_score']}")
        
        similarity_text = " | ".join(similarity_info) if similarity_info else "Similar content"
        
        # Display recommendation card
        st.markdown(f"""
        <div class="recommendation-card">
            <h4>#{i} - {rec['title']} ({rec.get('year', 'N/A')})</h4>
            <p style="font-style: italic; color: #FFD93D; margin: 0.8rem 0; font-size: 1.05rem;">
                "{rec.get('tagline', 'No tagline available')}"
            </p>
            <p style="font-size: 1rem; margin: 0.5rem 0;">
                <strong>⭐ Rating:</strong> <span style="color: #FFD93D;">{rec.get('rating', 'N/A')}/10</span>
            </p>
            <p style="font-size: 0.95rem; color: #4ECDC4; margin: 0.8rem 0;">
                <strong>🎯 Why recommended:</strong> {similarity_text}
            </p>
            <p style="font-size: 0.95rem; margin-top: 0.8rem;">
                <strong>🎭 Genres:</strong> {', '.join(rec.get('genres', [])) if rec.get('genres') else 'N/A'}
            </p>
        </div>
        """, unsafe_allow_html=True)


def visualize_knowledge_graph(engine: RecommendationEngine, movie_title: str):
    """
    Visualize the knowledge graph connections for a movie.
    
    Args:
        engine: RecommendationEngine instance
        movie_title: Title of the movie to visualize
    """
    st.markdown("### 🕸️ Knowledge Graph Visualization")
    st.markdown(f"*Showing connections for: **{movie_title}***")
    
    try:
        # Get graph data
        graph_data = engine.get_graph_visualization_data(movie_title)
        
        if not graph_data['nodes']:
            st.warning("No graph data available for this movie.")
            return
        
        # Convert to streamlit-agraph format
        nodes = []
        edges = []
        
        for node in graph_data['nodes']:
            nodes.append(Node(
                id=node['id'],
                label=node['label'],
                size=node.get('size', 20),
                color=node.get('color', '#97C2FC')
            ))
        
        for edge in graph_data['edges']:
            edges.append(Edge(
                source=edge['source'],
                target=edge['target'],
                label=edge.get('label', ''),
                color=edge.get('color', '#848484')
            ))
        
        # Configure graph visualization
        config = Config(
            width="100%",
            height=500,
            directed=True,
            physics=True,
            hierarchical=False,
            node={'labelProperty': 'label'},
            link={'labelProperty': 'label', 'renderLabel': True}
        )
        
        # Display graph
        agraph(nodes=nodes, edges=edges, config=config)
        
        # Add legend
        st.markdown("""
        **Legend:**
        - 🔴 Red: Movie
        - 🔵 Teal: Director
        - 🟢 Green: Actor
        - 🟡 Yellow: Genre
        """)
        
    except Exception as e:
        st.error(f"Error visualizing graph: {e}")
        st.info("Graph visualization requires the movie to be in the database with relationships.")


def display_comparison_section():
    """
    Display educational content comparing graph DB vs relational DB.
    """
    with st.expander("📚 Why Graph Databases? (Click to expand)"):
        st.markdown("""
        ### Graph Database vs Relational Database
        
        #### For Movie Recommendations:
        
        **Relational Database (SQL):**
        ```sql
        -- Complex JOIN query needed
        SELECT DISTINCT m2.*
        FROM movies m1
        JOIN movie_actors ma1 ON m1.id = ma1.movie_id
        JOIN movie_actors ma2 ON ma1.actor_id = ma2.actor_id
        JOIN movies m2 ON ma2.movie_id = m2.id
        WHERE m1.title = 'Inception'
          AND m2.id != m1.id
        -- Additional JOINs needed for genres...
        ```
        - Multiple complex JOINs
        - Slow for deep relationships
        - Rigid schema
        
        **Graph Database (Cypher):**
        ```cypher
        // Simple pattern matching
        MATCH (m:Movie {title: 'Inception'})
        MATCH (m)<-[:ACTED_IN]-(actor)-[:ACTED_IN]->(other)
        WHERE other <> m
        RETURN other
        ```
        - Natural representation
        - Fast traversal
        - Flexible relationships
        
        #### Key Advantages of Neo4j:
        1. **Performance**: O(1) relationship traversal vs O(n) JOINs
        2. **Flexibility**: Easy to add new relationship types
        3. **Query Simplicity**: Cypher is more intuitive
        4. **Scalability**: Better for highly connected data
        """)


def main():
    """Main application entry point."""
    
    # Initialize
    display_header()
    engine = get_recommendation_engine()
    
    # Check if engine initialized successfully
    if engine is None:
        st.error("🔴 Failed to connect to Neo4j database")
        st.warning("⚠️ The application cannot function without a database connection.")
        
        with st.expander("🔧 Azure Deployment Troubleshooting", expanded=True):
            st.markdown("""
            ### Common Azure Deployment Issues:
            
            1. **Environment Variables Not Set**
               - Ensure `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` are configured in Azure App Settings
               - Go to: Azure Portal → Your App Service → Configuration → Application Settings
            
            2. **Neo4j Connection Issues**
               - Verify Neo4j Aura instance is running
               - Check that Azure can reach your Neo4j instance (firewall rules)
               - Confirm Neo4j credentials are correct
            
            3. **Startup Script Issues**
               - Verify startup.sh has execute permissions
               - Check Azure logs: Azure Portal → Your App Service → Log stream
            
            4. **Port Configuration**
               - Azure automatically sets the PORT environment variable
               - Current PORT: Check Azure environment settings
            
            ### Debug Information:
            """)
            
            neo4j_uri = os.getenv('NEO4J_URI', 'Not set')
            neo4j_user = os.getenv('NEO4J_USERNAME', 'Not set')
            has_password = 'Yes' if os.getenv('NEO4J_PASSWORD') else 'No'
            port = os.getenv('PORT', 'Not set')
            
            st.code(f"""
Environment Variables Status:
- NEO4J_URI: {neo4j_uri}
- NEO4J_USERNAME: {neo4j_user}
- NEO4J_PASSWORD: {'***' if has_password == 'Yes' else 'Not set'}
- PORT: {port}
            """)
            
            st.info("""
            **Next Steps:**
            1. Set up Neo4j Aura at https://neo4j.com/cloud/aura/
            2. Add environment variables in Azure App Settings
            3. Restart the application
            4. Run data_seeder.py to populate the database
            """)
        
        st.stop()
    
    # Sidebar
    display_sidebar_stats(engine)
    
    # Main content
    try:
        # Get all movies for selection
        movies = engine.get_all_movies()
        
        if not movies:
            st.error("No movies found in database. Please run data_seeder.py first!")
            st.code("python data_seeder.py")
            st.stop()
        
        # Movie selection
        st.markdown("### 🎯 Select a Movie")
        movie_titles = [movie['title'] for movie in movies]
        selected_title = st.selectbox(
            "Choose a movie to get recommendations:",
            movie_titles,
            index=0
        )
        
        if selected_title:
            # Get movie details
            movie_details = engine.get_movie_details(selected_title)
            
            if movie_details:
                # Display movie info
                display_movie_details(movie_details)
                
                st.markdown("---")
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["🎯 Recommendations", "🕸️ Graph View", "📊 Analysis"])
                
                with tab1:
                    # Recommendation type selector
                    rec_type = st.radio(
                        "Recommendation Strategy:",
                        ["Combined (Best)", "By Genre", "By Cast"],
                        horizontal=True
                    )
                    
                    # Get recommendations based on selection
                    if rec_type == "Combined (Best)":
                        recommendations = engine.get_combined_recommendations(selected_title, limit=8)
                        display_recommendations(recommendations, "Combined - Genres & Cast")
                    elif rec_type == "By Genre":
                        recommendations = engine.get_similar_movies_by_genre(selected_title, limit=8)
                        display_recommendations(recommendations, "Genre-Based")
                    else:  # By Cast
                        recommendations = engine.get_similar_movies_by_cast(selected_title, limit=8)
                        display_recommendations(recommendations, "Cast-Based")
                
                with tab2:
                    visualize_knowledge_graph(engine, selected_title)
                
                with tab3:
                    st.markdown("### 📊 Detailed Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-number">{len(movie_details.get('cast', []))}</div>
                            <div class="stat-label">Cast Members</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-number">{len(movie_details.get('genres', []))}</div>
                            <div class="stat-label">Genres</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-number">{movie_details.get('rating', 0)}</div>
                            <div class="stat-label">IMDb Rating</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Show Cypher query examples
                    st.markdown("### 🔍 Cypher Queries Used")
                    st.code("""
// Find similar movies by shared actors
MATCH (selected:Movie {title: 'Inception'})
MATCH (selected)<-[:ACTED_IN]-(actor)-[:ACTED_IN]->(other)
WHERE other <> selected
WITH other, COUNT(DISTINCT actor) as shared_actors
RETURN other.title, shared_actors
ORDER BY shared_actors DESC
                    """, language="cypher")
        
        # Educational comparison
        st.markdown("---")
        display_comparison_section()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p>🎓 <strong>University Project</strong> - Demonstrating Graph Database Superiority</p>
            <p>Built with Neo4j, Python & Streamlit</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Application error: {e}", exc_info=True)
        
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common issues:**
            1. **Database connection failed**: Check your .env file
            2. **No data found**: Run `python data_seeder.py`
            3. **Import errors**: Run `pip install -r requirements.txt`
            
            **Need help?**
            - Ensure Neo4j is running
            - Verify .env credentials
            - Check Python version (3.10+ required)
            """)


if __name__ == "__main__":
    main()
