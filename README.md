# Postgres Natural Language Agent

An AI-powered voice and text agent for natural language-driven database interactions. This project enables users to query and modify a PostgreSQL database using natural conversational language, powered by Google's Agent Development Kit.

## 📌 Features

- 🔍 Natural language to SQL translation (CRUD operations)
- 🎙️ Voice and text input support
- 📊 Dynamic PostgreSQL database connectivity
- 🧠 Google Agent Development Kit (Dialogflow / Gemini APIs) for NLU
- 📈 Real-time data retrieval and response
- ⚙️ Extensible intent and entity mapping
- 🌐 Modern web interface with voice recording
- 🔒 Secure database connections with connection pooling

## 🛠️ Tech Stack

- **PostgreSQL** — Relational database
- **FastAPI** — Modern web framework for APIs
- **SQLAlchemy** — Database ORM and connection management
- **Google Cloud Speech-to-Text** — Voice input processing
- **Google Cloud Text-to-Speech** — Voice output (optional)
- **Google Cloud Dialogflow** — Natural language understanding
- **Google Gemini AI** — Advanced SQL generation
- **Poetry** — Dependency management
- **Uvicorn** — ASGI server

## 🚀 How It Works

1. User inputs a query via voice or text (e.g., *"Show me all orders from last week."*)
2. The agent processes the input using Google's NLU services (Dialogflow) or pattern matching
3. Detected intents and entities are mapped to predefined or dynamic SQL templates
4. SQL query is executed against the PostgreSQL database
5. Results are formatted and returned to the user through text and/or synthesized speech

## 📦 Installation

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Google Cloud account (for speech and NLU services)
- Poetry (for dependency management)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/postgres-nl-agent.git
cd postgres-nl-agent
```

### 2. Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Set Up Environment Variables

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Google Cloud Configuration
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# Optional: Dialogflow for advanced NLU
DIALOGFLOW_PROJECT_ID=your-dialogflow-project-id

# Optional: Gemini for advanced SQL generation
GEMINI_API_KEY=your-gemini-api-key
```

### 4. Set Up Google Cloud Services

#### Speech-to-Text and Text-to-Speech
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Speech-to-Text and Text-to-Speech APIs
4. Create a service account and download the JSON key file
5. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your key file

#### Dialogflow (Optional)
1. Go to [Dialogflow Console](https://dialogflow.cloud.google.com/)
2. Create a new agent
3. Set up intents for database queries
4. Note your project ID and set `DIALOGFLOW_PROJECT_ID`

#### Gemini AI (Optional)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Set `GEMINI_API_KEY` in your environment

### 5. Set Up Database

#### Option A: Use Sample Database
```bash
# Connect to your PostgreSQL instance
psql -U your_username -d your_database_name

# Run the setup script
\i scripts/setup_database.sql
```

#### Option B: Use Your Own Database
Ensure your database is accessible and the user has appropriate permissions.

### 6. Run the Application

```bash
# Activate the virtual environment
poetry shell

# Run the application
python main.py
```

The application will be available at `http://localhost:8000`

## 🎯 Usage Examples

### Text Queries
- "Show me all customers"
- "How many orders do we have?"
- "Display orders from last week"
- "Find customers with email containing 'example.com'"
- "What's the total revenue this month?"

### Voice Queries
Click the microphone button and speak your query naturally.

### API Endpoints

#### Text Query
```bash
curl -X POST "http://localhost:8000/query/text" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all customers"}'
```

#### Voice Query
```bash
curl -X POST "http://localhost:8000/query/voice" \
  -F "audio=@recording.wav"
```

#### Health Check
```bash
curl "http://localhost:8000/health"
```

## 📁 Project Structure

```
postgres-nl-agent/
├── main.py                 # Main FastAPI application
├── pyproject.toml         # Poetry configuration and dependencies
├── env.example            # Environment variables template
├── README.md              # This file
├── scripts/
│   └── setup_database.sql # Sample database setup
└── src/
    ├── __init__.py
    ├── agent/
    │   ├── __init__.py
    │   └── nlu_processor.py    # Natural language processing
    ├── database/
    │   ├── __init__.py
    │   └── postgres_manager.py # Database operations
    ├── speech/
    │   ├── __init__.py
    │   └── speech_handler.py   # Speech processing
    └── utils/
        ├── __init__.py
        └── config.py           # Configuration management
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_HOST` | PostgreSQL host | Yes | localhost |
| `DB_PORT` | PostgreSQL port | Yes | 5432 |
| `DB_NAME` | Database name | Yes | - |
| `DB_USER` | Database username | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `GOOGLE_PROJECT_ID` | Google Cloud project ID | Yes | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | Yes | - |
| `DIALOGFLOW_PROJECT_ID` | Dialogflow project ID | No | - |
| `GEMINI_API_KEY` | Gemini API key | No | - |
| `DEBUG` | Enable debug mode | No | False |

## 🧪 Testing

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run flake8
poetry run mypy .
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build the image
docker build -t postgres-nl-agent .

# Run the container
docker run -p 8000:8000 --env-file .env postgres-nl-agent
```

### Production Deployment
1. Set up a production PostgreSQL database
2. Configure Google Cloud services for production
3. Use a production ASGI server like Gunicorn
4. Set up reverse proxy (nginx)
5. Configure SSL certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the [Google Cloud documentation](https://cloud.google.com/docs) for service setup
- Review the [FastAPI documentation](https://fastapi.tiangolo.com/) for framework details

## 🔮 Roadmap

- [ ] Support for multiple database types (MySQL, SQLite)
- [ ] Advanced query builder with visual interface
- [ ] Query history and favorites
- [ ] Scheduled queries and alerts
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Integration with BI tools
- [ ] Mobile application
