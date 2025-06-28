# Postgres Natural Language Agent

An AI-powered voice and text agent for natural language-driven database interactions. This project enables users to query and modify a PostgreSQL database using natural conversational language, powered by Google's Agent Development Kit.

## 📌 Features

- 🔍 Natural language to SQL translation (CRUD operations)
- 🎙️ Voice and text input support
- 📊 Dynamic PostgreSQL database connectivity
- 🧠 Google Agent Development Kit (Dialogflow / Gemini APIs) for NLU
- 📈 Real-time data retrieval and response
- ⚙️ Extensible intent and entity mapping

## 🛠️ Tech Stack

- **PostgreSQL** — Relational database
- **Google Agent Development Kit** — NLU agent backend
- **Python / Node.js (select your preference)** — Agent runtime
- **Speech-to-Text API (Google Cloud)** — For voice input handling
- **Text-to-Speech API (optional)** — For voice responses

## 🚀 How It Works

1. User inputs a query via voice or text (e.g., *"Show me all orders from last week."*)
2. The agent processes the input using Google's NLU services.
3. Detected intents and entities are mapped to predefined or dynamic SQL templates.
4. SQL query is executed against the PostgreSQL database.
5. Results are formatted and returned to the user through text and/or synthesized speech.

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/postgres-nl-agent.git
   cd postgres-nl-agent
