"""
Configuration management for the Postgres NL Agent
"""

import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Configuration class for managing application settings"""
    
    def __init__(self):
        load_dotenv()
        
        # Database configuration
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "5432"))
        self.db_name = os.getenv("DB_NAME", "postgres")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_url = os.getenv("DATABASE_URL")
        
        # Google Cloud configuration
        self.google_project_id = os.getenv("GOOGLE_PROJECT_ID")
        self.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # Dialogflow configuration
        self.dialogflow_project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
        self.dialogflow_session_id = os.getenv("DIALOGFLOW_SESSION_ID", "default-session")
        self.dialogflow_language_code = os.getenv("DIALOGFLOW_LANGUAGE_CODE", "en-US")
        
        # Gemini configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Speech configuration
        self.speech_language_code = os.getenv("SPEECH_LANGUAGE_CODE", "en-US")
        self.speech_encoding = os.getenv("SPEECH_ENCODING", "LINEAR16")
        self.speech_sample_rate = int(os.getenv("SPEECH_SAMPLE_RATE", "16000"))
        
        # Application configuration
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
    def get_database_url(self) -> str:
        """Get the database connection URL"""
        if self.db_url:
            return self.db_url
        
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        required_vars = [
            "DB_NAME",
            "DB_USER", 
            "DB_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True 