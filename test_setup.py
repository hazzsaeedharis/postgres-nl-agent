#!/usr/bin/env python3
"""
Test script to verify Postgres NL Agent setup
"""

import sys
import os
import asyncio
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        from google.cloud import speech_v1
        print("✅ Google Cloud Speech imported successfully")
    except ImportError as e:
        print(f"❌ Google Cloud Speech import failed: {e}")
        return False
    
    try:
        from google.cloud import dialogflow_v2
        print("✅ Google Cloud Dialogflow imported successfully")
    except ImportError as e:
        print(f"❌ Google Cloud Dialogflow import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test that project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "main.py",
        "pyproject.toml",
        "env.example",
        "src/__init__.py",
        "src/agent/__init__.py",
        "src/agent/nlu_processor.py",
        "src/database/__init__.py",
        "src/database/postgres_manager.py",
        "src/speech/__init__.py",
        "src/speech/speech_handler.py",
        "src/utils/__init__.py",
        "src/utils/config.py",
        "scripts/setup_database.sql"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n⚙️ Testing environment configuration...")
    
    # Check if .env file exists
    if Path(".env").exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found - you'll need to create one from env.example")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 12):
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} is too old. Need 3.12+")
        return False
    
    return True

async def test_components():
    """Test that components can be initialized"""
    print("\n🧪 Testing component initialization...")
    
    try:
        from src.utils.config import Config
        config = Config()
        print("✅ Config component initialized")
    except Exception as e:
        print(f"❌ Config component failed: {e}")
        return False
    
    try:
        from src.agent.nlu_processor import NLUProcessor
        nlu = NLUProcessor()
        print("✅ NLU Processor initialized")
    except Exception as e:
        print(f"❌ NLU Processor failed: {e}")
        return False
    
    try:
        from src.database.postgres_manager import PostgresManager
        db_manager = PostgresManager()
        print("✅ Database Manager initialized")
    except Exception as e:
        print(f"❌ Database Manager failed: {e}")
        return False
    
    try:
        from src.speech.speech_handler import SpeechHandler
        speech = SpeechHandler()
        print("✅ Speech Handler initialized")
    except Exception as e:
        print(f"❌ Speech Handler failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Postgres NL Agent Setup Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install dependencies with: poetry install")
        return False
    
    # Test project structure
    if not test_project_structure():
        print("\n❌ Project structure test failed.")
        return False
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed.")
        return False
    
    # Test components
    if not asyncio.run(test_components()):
        print("\n❌ Component initialization test failed.")
        return False
    
    print("\n🎉 All tests passed! Your Postgres NL Agent is ready to use.")
    print("\nNext steps:")
    print("1. Copy env.example to .env and configure your settings")
    print("2. Set up your PostgreSQL database")
    print("3. Configure Google Cloud services")
    print("4. Run: python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 