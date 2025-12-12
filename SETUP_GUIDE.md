# Setup Guide for Movie Recommendation System

## 🎯 Complete Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Neo4j Database (Choose one):
  - **Neo4j Aura (Cloud)**: Free tier available at https://neo4j.com/cloud/aura/
  - **Local Neo4j**: Download from https://neo4j.com/download/

### Step 1: Get Neo4j Credentials

#### Option A: Neo4j Aura (Cloud - Recommended for Beginners)
1. Go to https://neo4j.com/cloud/aura/
2. Sign up for a free account
3. Create a new database instance
4. Save the credentials (URI, username, password)
5. **Important**: Download or copy the password - you won't see it again!

Your credentials will look like:
```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-generated-password
```

#### Option B: Local Neo4j
1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and create a new database
3. Start the database
4. Default credentials:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j (or your custom password)
```

### Step 2: Clone and Setup Project

```bash
# Navigate to project directory
cd Smart_Movie_Recommendation_Engine

# Option A: Use setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Option B: Manual setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your actual Neo4j credentials
nano .env  # or use any text editor
```

Update the `.env` file:
```env
NEO4J_URI=neo4j+s://your-actual-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-actual-password
```

### Step 4: Test Database Connection

```bash
# Test if connection works
python db_connection.py
```

Expected output:
```
✓ Successfully connected to Neo4j database
✓ Connection test passed!
✓ Connection verification passed!
```

If you see errors:
- Check your .env credentials
- Ensure Neo4j is running (local) or accessible (cloud)
- Verify firewall settings

### Step 5: Seed Database with Sample Data

```bash
python data_seeder.py
```

This will:
- Clear existing data (if any)
- Create 10 movies
- Create 10 people (actors and directors)
- Create 5 genres
- Establish all relationships

Expected output:
```
🌱 Starting Data Seeding Process
✓ Database cleared successfully
✓ Created 5 genres
✓ Created 10 people
✓ Created 10 movies
✓ Created relationships
✅ Data Seeding Complete!
```

### Step 6: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🧪 Testing

### Test Recommendation Engine
```bash
python recommendation_engine.py
```

### Verify Data in Neo4j Browser
If using local Neo4j:
1. Open Neo4j Browser at http://localhost:7474
2. Login with your credentials
3. Run query: `MATCH (n) RETURN n LIMIT 25`

If using Neo4j Aura:
1. Go to your Aura console
2. Click "Query" button
3. Run query: `MATCH (n) RETURN n LIMIT 25`

## 📊 Sample Cypher Queries for Your Presentation

Copy these into Neo4j Browser to impress your professors!

### 1. View All Movies
```cypher
MATCH (m:Movie)
RETURN m.title, m.year, m.rating
ORDER BY m.rating DESC
```

### 2. Find Movies by Actor
```cypher
MATCH (actor:Person {name: 'Leonardo DiCaprio'})-[:ACTED_IN]->(movie:Movie)
RETURN actor.name, movie.title, movie.year
```

### 3. Find Similar Movies (The Core Logic!)
```cypher
MATCH (selected:Movie {title: 'Inception'})
MATCH (selected)<-[:ACTED_IN]-(actor)-[:ACTED_IN]->(other)
WHERE other <> selected
WITH other, COUNT(DISTINCT actor) as shared_actors
RETURN other.title, shared_actors
ORDER BY shared_actors DESC
```

### 4. Show Full Knowledge Graph
```cypher
MATCH (m:Movie {title: 'Inception'})
OPTIONAL MATCH (director:Person)-[:DIRECTED]->(m)
OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(m)
OPTIONAL MATCH (m)-[:IN_GENRE]->(genre:Genre)
RETURN m, director, actor, genre
```

### 5. Find Movies in Multiple Genres
```cypher
MATCH (m:Movie)-[:IN_GENRE]->(g:Genre)
WHERE g.name IN ['Sci-Fi', 'Action']
RETURN m.title, COLLECT(g.name) as genres
```

## 🎓 For Your Viva/Presentation

### Key Points to Mention:

1. **Why Graph Database?**
   - Natural representation of relationships
   - O(1) traversal vs O(n) JOINs
   - Flexible schema - easy to add new relationship types

2. **Knowledge Graph Structure:**
   - Nodes: Movies, People, Genres
   - Relationships: ACTED_IN, DIRECTED, IN_GENRE
   - Properties: title, name, year, rating, etc.

3. **Recommendation Algorithm:**
   - Pattern matching using Cypher
   - Finds movies with shared actors/genres
   - Weighted scoring system
   - Real-time graph traversal

4. **Advantages over SQL:**
   - Simpler queries (show comparison in app)
   - Better performance for connected data
   - More intuitive for recommendation systems

## 🔧 Troubleshooting

### "Failed to connect to Neo4j"
- Check .env file exists and has correct credentials
- Verify Neo4j is running (local) or accessible (cloud)
- Test connection: `python db_connection.py`

### "No module named 'neo4j'"
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment if using one

### "No movies found in database"
- Run data seeder: `python data_seeder.py`
- Verify data: Check Neo4j Browser

### Streamlit not opening
- Check if port 8501 is available
- Try: `streamlit run app.py --server.port 8502`

### Graph visualization not showing
- Install: `pip install streamlit-agraph`
- Restart Streamlit

## 📚 Additional Resources

- Neo4j Documentation: https://neo4j.com/docs/
- Cypher Query Language: https://neo4j.com/docs/cypher-manual/
- Streamlit Documentation: https://docs.streamlit.io/

## 🎬 Demo Flow for Presentation

1. Show the Streamlit UI
2. Select a movie (e.g., "Inception")
3. Show movie details
4. Display recommendations
5. Show graph visualization
6. Open Neo4j Browser
7. Run Cypher queries
8. Explain the graph structure
9. Compare with SQL equivalent (in app)

## 📝 Project Structure Explanation

```
Smart_Movie_Recommendation_Engine/
├── db_connection.py          # Handles Neo4j connections (singleton pattern)
├── data_seeder.py            # Populates database with sample data
├── recommendation_engine.py  # Core recommendation logic
├── app.py                    # Streamlit UI
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (not in git)
├── README.md                 # Project overview
└── SETUP_GUIDE.md           # This file
```

Good luck with your presentation! 🎓
