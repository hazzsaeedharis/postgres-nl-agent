"""
Natural Language Understanding (NLU) processor for converting natural language to SQL
"""

import logging
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from google.cloud import dialogflow_v2
from google.cloud.dialogflow_v2 import SessionsClient, TextInput

from src.utils.config import Config

logger = logging.getLogger(__name__)

class NLUProcessor:
    """Processes natural language queries and converts them to SQL"""
    
    def __init__(self):
        self.config = Config()
        self._setup_services()
        
        # Common SQL patterns and templates
        self.sql_templates = {
            "select": "SELECT {columns} FROM {table} {where} {order_by} {limit}",
            "count": "SELECT COUNT(*) FROM {table} {where}",
            "insert": "INSERT INTO {table} ({columns}) VALUES ({values})",
            "update": "UPDATE {table} SET {set_clause} {where}",
            "delete": "DELETE FROM {table} {where}"
        }
        
        # Intent patterns
        self.intent_patterns = {
            "select_data": [
                r"show me", r"display", r"get", r"find", r"list", r"what", r"how many",
                r"select", r"retrieve", r"fetch", r"see", r"view"
            ],
            "count_data": [
                r"count", r"how many", r"total number", r"number of"
            ],
            "insert_data": [
                r"add", r"insert", r"create", r"new", r"add new"
            ],
            "update_data": [
                r"update", r"modify", r"change", r"edit", r"set"
            ],
            "delete_data": [
                r"delete", r"remove", r"drop", r"clear"
            ]
        }
    
    def _setup_services(self):
        """Setup Google Cloud services"""
        try:
            # Setup Gemini
            if self.config.gemini_api_key:
                genai.configure(api_key=self.config.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            else:
                self.gemini_model = None
                logger.warning("Gemini API key not configured")
            
            # Setup Dialogflow
            if self.config.dialogflow_project_id:
                self.dialogflow_client = SessionsClient()
            else:
                self.dialogflow_client = None
                logger.warning("Dialogflow project ID not configured")
                
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
    
    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process natural language text to extract intent and entities"""
        try:
            # Try Dialogflow first if available
            if self.dialogflow_client:
                result = await self._process_with_dialogflow(text)
                if result:
                    return result
            
            # Fallback to pattern matching
            return await self._process_with_patterns(text)
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.5,
                "entities": {},
                "original_text": text
            }
    
    async def _process_with_dialogflow(self, text: str) -> Optional[Dict[str, Any]]:
        """Process text using Dialogflow"""
        try:
            session_path = self.dialogflow_client.session_path(
                self.config.dialogflow_project_id,
                self.config.dialogflow_session_id
            )
            
            text_input = TextInput(
                text=text,
                language_code=self.config.dialogflow_language_code
            )
            
            request = dialogflow_v2.DetectIntentRequest(
                session=session_path,
                query_input=text_input
            )
            
            response = self.dialogflow_client.detect_intent(request=request)
            
            return {
                "intent": response.query_result.intent.display_name,
                "confidence": response.query_result.intent_detection_confidence,
                "entities": {
                    param.display_name: param.value
                    for param in response.query_result.parameters.fields
                },
                "original_text": text
            }
            
        except Exception as e:
            logger.error(f"Dialogflow processing error: {e}")
            return None
    
    async def _process_with_patterns(self, text: str) -> Dict[str, Any]:
        """Process text using pattern matching"""
        text_lower = text.lower()
        
        # Determine intent
        intent = "unknown"
        confidence = 0.5
        
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    intent = intent_name
                    confidence = 0.8
                    break
            if intent != "unknown":
                break
        
        # Extract basic entities (simplified)
        entities = self._extract_entities(text)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "original_text": text
        }
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using simple patterns"""
        entities = {}
        text_lower = text.lower()
        
        # Extract table names (common patterns)
        table_patterns = [
            r"from\s+(\w+)",
            r"table\s+(\w+)",
            r"in\s+(\w+)",
        ]
        
        for pattern in table_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities["table"] = match.group(1)
                break
        
        # Extract time references
        time_patterns = {
            "last_week": r"last\s+week",
            "last_month": r"last\s+month",
            "yesterday": r"yesterday",
            "today": r"today",
            "this_week": r"this\s+week",
            "this_month": r"this\s+month"
        }
        
        for time_key, pattern in time_patterns.items():
            if re.search(pattern, text_lower):
                entities["time_period"] = time_key
                break
        
        # Extract numbers
        number_match = re.search(r"(\d+)", text)
        if number_match:
            entities["number"] = int(number_match.group(1))
        
        return entities
    
    async def generate_sql(self, nlu_result: Dict[str, Any]) -> str:
        """Generate SQL query from NLU result"""
        try:
            intent = nlu_result.get("intent", "unknown")
            entities = nlu_result.get("entities", {})
            
            # Use Gemini for advanced SQL generation if available
            if self.gemini_model:
                return await self._generate_sql_with_gemini(nlu_result)
            
            # Fallback to template-based generation
            return self._generate_sql_with_templates(intent, entities)
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return "SELECT 1"  # Safe fallback
    
    async def _generate_sql_with_gemini(self, nlu_result: Dict[str, Any]) -> str:
        """Generate SQL using Gemini AI"""
        try:
            prompt = f"""
            Convert this natural language query to SQL:
            
            Query: {nlu_result['original_text']}
            Intent: {nlu_result['intent']}
            Entities: {nlu_result['entities']}
            
            Generate a valid PostgreSQL query. Only return the SQL query, nothing else.
            """
            
            response = self.gemini_model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Basic validation
            if not sql_query.lower().startswith(('select', 'insert', 'update', 'delete')):
                raise ValueError("Invalid SQL generated")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Gemini SQL generation error: {e}")
            return self._generate_sql_with_templates(
                nlu_result.get("intent", "unknown"),
                nlu_result.get("entities", {})
            )
    
    def _generate_sql_with_templates(self, intent: str, entities: Dict[str, Any]) -> str:
        """Generate SQL using predefined templates"""
        table = entities.get("table", "unknown_table")
        
        if intent == "select_data":
            columns = "*"
            where_clause = ""
            order_clause = ""
            limit_clause = ""
            
            # Add time-based filtering
            if "time_period" in entities:
                time_period = entities["time_period"]
                if time_period == "last_week":
                    where_clause = "WHERE created_at >= NOW() - INTERVAL '7 days'"
                elif time_period == "last_month":
                    where_clause = "WHERE created_at >= NOW() - INTERVAL '1 month'"
                elif time_period == "today":
                    where_clause = "WHERE DATE(created_at) = CURRENT_DATE"
            
            return self.sql_templates["select"].format(
                columns=columns,
                table=table,
                where=where_clause,
                order_by=order_clause,
                limit=limit_clause
            )
        
        elif intent == "count_data":
            where_clause = ""
            if "time_period" in entities:
                time_period = entities["time_period"]
                if time_period == "last_week":
                    where_clause = "WHERE created_at >= NOW() - INTERVAL '7 days'"
            
            return self.sql_templates["count"].format(
                table=table,
                where=where_clause
            )
        
        else:
            # Default to SELECT for unknown intents
            return f"SELECT * FROM {table} LIMIT 10"
    
    async def generate_response(self, nlu_result: Dict[str, Any], query_result: Any) -> str:
        """Generate natural language response from query results"""
        try:
            intent = nlu_result.get("intent", "unknown")
            
            if intent == "count_data":
                if isinstance(query_result, list) and len(query_result) > 0:
                    count = query_result[0].get("count", 0)
                    return f"I found {count} records."
                return "I couldn't count the records."
            
            elif intent == "select_data":
                if isinstance(query_result, list):
                    count = len(query_result)
                    if count == 0:
                        return "No records found."
                    elif count == 1:
                        return f"I found 1 record."
                    else:
                        return f"I found {count} records."
                return "I couldn't retrieve the data."
            
            else:
                return "Query executed successfully."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Query completed." 