#!/usr/bin/env python3
"""
Postgres Natural Language Agent
Main application entry point
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from src.agent.nlu_processor import NLUProcessor
from src.database.postgres_manager import PostgresManager
from src.speech.speech_handler import SpeechHandler
from src.utils.config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Postgres Natural Language Agent",
    description="AI-powered voice and text agent for natural language-driven database interactions",
    version="0.1.0"
)

# Initialize components
config = Config()
nlu_processor = NLUProcessor()
postgres_manager = PostgresManager()
speech_handler = SpeechHandler()

class QueryRequest(BaseModel):
    """Request model for text queries"""
    query: str
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for queries"""
    query: str
    sql_generated: str
    result: Any
    confidence: float
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        await postgres_manager.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await postgres_manager.disconnect()
    logger.info("Database connection closed")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Postgres NL Agent</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .input-group { margin: 20px 0; }
            input[type="text"], textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .voice-controls { text-align: center; margin: 20px 0; }
            .record-btn { background: #dc3545; }
            .record-btn.recording { background: #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗄️ Postgres Natural Language Agent</h1>
            <p>Ask questions about your database in natural language!</p>
            
            <div class="voice-controls">
                <button id="recordBtn" class="record-btn" onclick="toggleRecording()">🎤 Start Recording</button>
                <div id="status">Click to start voice recording</div>
            </div>
            
            <div class="input-group">
                <label for="query">Or type your query:</label>
                <textarea id="query" rows="3" placeholder="e.g., 'Show me all orders from last week' or 'How many customers do we have?'"></textarea>
                <button onclick="sendQuery()">Send Query</button>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            let isRecording = false;
            let mediaRecorder;
            let audioChunks = [];
            
            async function toggleRecording() {
                if (!isRecording) {
                    await startRecording();
                } else {
                    stopRecording();
                }
            }
            
            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        await sendVoiceQuery(audioBlob);
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    document.getElementById('recordBtn').textContent = '⏹️ Stop Recording';
                    document.getElementById('recordBtn').classList.add('recording');
                    document.getElementById('status').textContent = 'Recording... Speak now!';
                } catch (err) {
                    console.error('Error accessing microphone:', err);
                    alert('Error accessing microphone. Please check permissions.');
                }
            }
            
            function stopRecording() {
                if (mediaRecorder && isRecording) {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    isRecording = false;
                    document.getElementById('recordBtn').textContent = '🎤 Start Recording';
                    document.getElementById('recordBtn').classList.remove('recording');
                    document.getElementById('status').textContent = 'Processing audio...';
                }
            }
            
            async function sendVoiceQuery(audioBlob) {
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.wav');
                
                try {
                    const response = await fetch('/query/voice', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    displayResult(result);
                } catch (err) {
                    console.error('Error sending voice query:', err);
                    document.getElementById('status').textContent = 'Error processing voice query';
                }
            }
            
            async function sendQuery() {
                const query = document.getElementById('query').value.trim();
                if (!query) return;
                
                try {
                    const response = await fetch('/query/text', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    const result = await response.json();
                    displayResult(result);
                } catch (err) {
                    console.error('Error sending query:', err);
                }
            }
            
            function displayResult(result) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `
                    <div class="result">
                        <h3>Query: ${result.query}</h3>
                        <p><strong>Generated SQL:</strong> <code>${result.sql_generated}</code></p>
                        <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                        <p><strong>Result:</strong></p>
                        <pre>${JSON.stringify(result.result, null, 2)}</pre>
                        <p><strong>Message:</strong> ${result.message}</p>
                    </div>
                `;
                document.getElementById('status').textContent = 'Query completed';
            }
        </script>
    </body>
    </html>
    """

@app.post("/query/text", response_model=QueryResponse)
async def process_text_query(request: QueryRequest):
    """Process a text-based natural language query"""
    try:
        logger.info(f"Processing text query: {request.query}")
        
        # Process natural language to extract intent and entities
        nlu_result = await nlu_processor.process_text(request.query)
        
        # Generate SQL from NLU result
        sql_query = await nlu_processor.generate_sql(nlu_result)
        
        # Execute SQL query
        result = await postgres_manager.execute_query(sql_query)
        
        # Generate response message
        message = await nlu_processor.generate_response(nlu_result, result)
        
        return QueryResponse(
            query=request.query,
            sql_generated=sql_query,
            result=result,
            confidence=nlu_result.get('confidence', 0.8),
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error processing text query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/voice", response_model=QueryResponse)
async def process_voice_query(audio: UploadFile = File(...)):
    """Process a voice-based natural language query"""
    try:
        logger.info(f"Processing voice query from file: {audio.filename}")
        
        # Convert speech to text
        text_query = await speech_handler.speech_to_text(audio)
        
        # Process the text query
        nlu_result = await nlu_processor.process_text(text_query)
        
        # Generate SQL from NLU result
        sql_query = await nlu_processor.generate_sql(nlu_result)
        
        # Execute SQL query
        result = await postgres_manager.execute_query(sql_query)
        
        # Generate response message
        message = await nlu_processor.generate_response(nlu_result, result)
        
        return QueryResponse(
            query=text_query,
            sql_generated=sql_query,
            result=result,
            confidence=nlu_result.get('confidence', 0.8),
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": await postgres_manager.is_connected()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
