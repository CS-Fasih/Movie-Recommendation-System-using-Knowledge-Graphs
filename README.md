# 🎬 Smart Movie Recommendation Engine
## Knowledge Graph-Based Movie Recommendations using Neo4j

A university project demonstrating the power of graph databases over relational databases for recommendation systems.

### 🎯 Project Overview
This system uses Neo4j's graph database to model movies, actors, directors, and genres as interconnected nodes, enabling intelligent recommendations based on shared relationships.

### 🏗️ Knowledge Graph Schema

**Nodes:**
- `Movie`: Films in our database
- `Person`: Actors and Directors
- `Genre`: Movie categories

**Relationships:**
- `(:Person)-[:ACTED_IN]->(:Movie)` - Actor appears in a movie
- `(:Person)-[:DIRECTED]->(:Movie)` - Director helms a movie
- `(:Movie)-[:IN_GENRE]->(:Genre)` - Movie belongs to a genre

### 🚀 Quick Start

#### Prerequisites
- Python 3.10+
- Neo4j Database (Aura Cloud or Local instance)

#### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd Smart_Movie_Recommendation_Engine
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection:**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j credentials
   ```

4. **Seed the database:**
   ```bash
   python data_seeder.py
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

### 📁 Project Structure
```
Smart_Movie_Recommendation_Engine/
├── db_connection.py       # Neo4j connection manager
├── data_seeder.py         # Sample data insertion script
├── recommendation_engine.py  # Recommendation logic & Cypher queries
├── app.py                 # Streamlit UI
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

### 🎓 Academic Value
This project demonstrates:
- Graph database advantages for interconnected data
- Cypher query language for pattern matching
- Real-world application of graph traversal algorithms
- Scalable recommendation system architecture

### 📊 Features
- Interactive movie selection
- Relationship-based recommendations
- Visual graph representation
- Real-time queries on Neo4j

### 🔧 Technology Stack
- **Database:** Neo4j (Graph Database)
- **Backend:** Python 3.10+
- **Frontend:** Streamlit
- **Visualization:** streamlit-agraph

---
**Built for educational purposes - demonstrating graph database superiority in recommendation systems**
