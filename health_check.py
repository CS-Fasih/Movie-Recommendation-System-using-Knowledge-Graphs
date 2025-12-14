#!/usr/bin/env python3
"""
Health Check Script for Azure Deployment
=========================================

This script verifies that the application is properly configured
and can connect to Neo4j. Run this after deployment to diagnose issues.

Usage:
    python health_check.py
"""

import os
import sys
from dotenv import load_dotenv

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def check_environment_variables():
    """Check if required environment variables are set."""
    print_section("Environment Variables Check")
    
    load_dotenv()
    
    required_vars = {
        'NEO4J_URI': os.getenv('NEO4J_URI'),
        'NEO4J_USERNAME': os.getenv('NEO4J_USERNAME'),
        'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD')
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # Don't print actual password
            display_value = '***' if 'PASSWORD' in var_name else var_value
            print(f"✓ {var_name}: {display_value}")
        else:
            print(f"✗ {var_name}: NOT SET")
            all_set = False
    
    # Check optional PORT variable
    port = os.getenv('PORT', '8000')
    print(f"ℹ PORT: {port} (default: 8000)")
    
    return all_set

def check_python_version():
    """Check Python version."""
    print_section("Python Version Check")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("✓ Python version is compatible (3.10+)")
        return True
    else:
        print("✗ Python version should be 3.10 or higher")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print_section("Dependencies Check")
    
    required_packages = [
        ('neo4j', '5.15.0'),
        ('streamlit', '1.29.0'),
        ('python-dotenv', '1.0.0'),
        ('streamlit_agraph', '0.0.45'),
        ('pandas', '2.1.4')
    ]
    
    all_installed = True
    for package_name, expected_version in required_packages:
        try:
            # Map package names to module names
            module_map = {
                'python-dotenv': 'dotenv',
                'streamlit_agraph': 'streamlit_agraph'
            }
            module_name = module_map.get(package_name, package_name)
            
            pkg = __import__(module_name)
            
            version = getattr(pkg, '__version__', 'unknown')
            print(f"✓ {package_name}: {version}")
        except ImportError:
            print(f"✗ {package_name}: NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_neo4j_connection():
    """Test Neo4j database connection."""
    print_section("Neo4j Connection Check")
    
    try:
        from db_connection import get_db_connection
        
        db = get_db_connection()
        print(f"ℹ Attempting to connect to: {db.uri}")
        
        if db.connect():
            print("✓ Successfully connected to Neo4j")
            
            if db.verify_connection():
                print("✓ Connection verification passed")
                
                # Get some basic stats
                stats_query = """
                MATCH (m:Movie) WITH count(m) as movies
                MATCH (p:Person) WITH movies, count(p) as people
                MATCH (g:Genre) WITH movies, people, count(g) as genres
                RETURN movies, people, genres
                """
                result = db.execute_query(stats_query)
                
                if result:
                    stats = result[0]
                    print(f"ℹ Database statistics:")
                    print(f"  - Movies: {stats.get('movies', 0)}")
                    print(f"  - People: {stats.get('people', 0)}")
                    print(f"  - Genres: {stats.get('genres', 0)}")
                    
                    if stats.get('movies', 0) == 0:
                        print("⚠ Database is empty! Run: python data_seeder.py")
                        return False
                
                db.close()
                return True
            else:
                print("✗ Connection verification failed")
                return False
        else:
            print("✗ Failed to connect to Neo4j")
            print("\nPossible issues:")
            print("  1. NEO4J_URI is incorrect or Neo4j is not running")
            print("  2. NEO4J_USERNAME or NEO4J_PASSWORD is wrong")
            print("  3. Network/firewall blocking connection")
            print("  4. Neo4j Aura instance is paused or deleted")
            return False
            
    except Exception as e:
        print(f"✗ Error checking Neo4j connection: {e}")
        return False

def check_streamlit_config():
    """Check Streamlit configuration."""
    print_section("Streamlit Configuration Check")
    
    config_file = ".streamlit/config.toml"
    if os.path.exists(config_file):
        print(f"✓ Streamlit config file exists: {config_file}")
        with open(config_file, 'r') as f:
            print("\nCurrent configuration:")
            print(f.read())
        return True
    else:
        print(f"⚠ Streamlit config file not found: {config_file}")
        print("  This is optional, but recommended for Azure deployment")
        return True

def check_startup_script():
    """Check if startup script exists and is executable."""
    print_section("Startup Script Check")
    
    startup_script = "startup.sh"
    if os.path.exists(startup_script):
        print(f"✓ Startup script exists: {startup_script}")
        
        # Check if executable on Unix-like systems
        if os.name != 'nt':  # Not Windows
            if os.access(startup_script, os.X_OK):
                print("✓ Startup script is executable")
            else:
                print("⚠ Startup script is not executable")
                print("  Run: chmod +x startup.sh")
        
        return True
    else:
        print(f"✗ Startup script not found: {startup_script}")
        return False

def main():
    """Run all health checks."""
    print("\n" + "=" * 60)
    print("Movie Recommendation System - Health Check")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment Variables", check_environment_variables),
        ("Dependencies", check_dependencies),
        ("Streamlit Configuration", check_streamlit_config),
        ("Startup Script", check_startup_script),
        ("Neo4j Connection", check_neo4j_connection)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n✗ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print_section("Health Check Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your application is ready to run.")
        print("\nTo start the application:")
        print("  Local: streamlit run app.py")
        print("  Azure: Should start automatically via startup.sh")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        print("\nCommon solutions:")
        print("  1. Set environment variables in Azure App Settings")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. Run: python data_seeder.py (to populate database)")
        print("  4. Check Neo4j Aura instance is running")
        return 1

if __name__ == "__main__":
    sys.exit(main())
