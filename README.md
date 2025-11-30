# Email Assistant - AI-Powered Email Query System

An intelligent email assistant that fetches, indexes, and allows natural language querying of your Gmail emails using AI-powered vector search and Google's Gemini model.

## Features

- **Email Fetching**: Automatically fetch emails from Gmail using IMAP
- **Vector Storage**: Index emails using ChromaDB for semantic search
- **AI-Powered Queries**: Ask natural language questions using Ollama (llama3.1:8b)
- **Local LLM**: No external API calls - runs completely on your machine
- **Interactive CLI**: User-friendly command-line interface
- **Persistent Storage**: Vector store persists between sessions
- **Configurable**: Easy configuration via environment variables

## Architecture

```
email_assistant.py (Main CLI Orchestrator)
    ├── agent_email_fetch.py     (Email fetching via IMAP)
    ├── agent_email_vector.py    (Vector store creation)
    ├── agent_email_query.py     (Natural language querying)
    ├── agent_email_workflow.py  (Workflow orchestration)
    └── config.py                (Configuration management)
```

## Workflow Chain

```
1. Fetch → Retrieves emails from Gmail (IMAP)
           ↓
2. Vector → Cleans and indexes emails in ChromaDB
           ↓
3. Query → Semantic search + LLM-powered responses
```

## Installation

### Prerequisites

- Python 3.9 or higher (required for LangChain v0.3)
- Gmail account with App Password enabled
- Ollama installed and running locally
- llama3.1:8b model pulled in Ollama

### Setup

1. **Install Ollama**

Visit [https://ollama.ai](https://ollama.ai) and download Ollama for your platform.

After installation, pull the required model:

```bash
ollama pull llama3.1:8b
```

Verify Ollama is running:

```bash
ollama list
```

2. **Clone or download the project**

```bash
cd email-assistant
```

3. **Create and activate virtual environment**

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Configure environment variables**

Copy `.env.example.new` to create your `.env` file:

```bash
# On Windows
copy .env.example.new .env

# On macOS/Linux
cp .env.example.new .env
```

Edit `.env` and fill in your credentials:

```env
# Email Configuration
EMAIL_ID=your-email@gmail.com
APP_PASSWORD=your-gmail-app-password

# Date Range for Email Fetching
START_DATE=2025-11-26
END_DATE=2025-11-28

# Ollama Configuration (defaults should work if Ollama is running locally)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=llama3.1:8b
```

### Getting Gmail App Password

1. Go to your Google Account settings
2. Enable 2-Step Verification
3. Go to Security → 2-Step Verification → App passwords
4. Generate a new app password for "Mail"
5. Use this 16-character password in your `.env` file

### Ollama Models

The system uses `llama3.1:8b` for both LLM and embeddings by default. You can use different models:

**For LLM (text generation):**
- llama3.1:8b (default, good balance)
- llama3.1:70b (more powerful, requires more resources)
- llama2:13b (alternative)

**For Embeddings:**
- llama3.1:8b (default, works well)
- nomic-embed-text (specialized embedding model, recommended)
- all-minilm (lightweight alternative)

To pull alternative models:

```bash
ollama pull nomic-embed-text
```

Then update your `.env`:

```env
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## Usage

### 1. Check System Status

```bash
python email_assistant.py status
```

Shows configuration validation and vector store information.

### 2. Fetch and Index Emails

```bash
# Use dates from .env file
python email_assistant.py refresh

# Specify custom date range
python email_assistant.py refresh --start 2025-11-01 --end 2025-11-28
```

This command:
- Fetches emails from Gmail
- Cleans and processes email content
- Creates a ChromaDB vector store
- Persists to disk for future queries

### 3. Query Your Emails

```bash
# Interactive mode
python email_assistant.py query

# Single question mode
python email_assistant.py query --question "Summarize my emails"
python email_assistant.py query -q "How many emails did I receive?"
```

Example queries:
- "How many emails did I receive?"
- "Summarize my emails"
- "Did I receive any important emails?"
- "List all senders"
- "What emails are about project updates?"
- "Find emails from john@example.com"

### 4. Complete Workflow

```bash
python email_assistant.py workflow
```

Runs the entire chain:
1. Fetches and indexes emails
2. Launches interactive query mode

Perfect for first-time setup!

## Project Structure

```
email-assistant/
│
├── email_assistant.py          # Main CLI application
├── config.py                   # Configuration management
│
├── agent_email_fetch.py        # Email fetching module
├── agent_email_vector.py       # Vector store creation
├── agent_email_query.py        # Query interface
├── agent_email_workflow.py     # Workflow orchestration
│
├── requirements.txt            # Python dependencies
├── .env.example               # Configuration template
├── .env                       # Your configuration (create this)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
│
└── chroma_store/              # Vector database (auto-created)
```

## Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_ID` | Your Gmail address | Required |
| `APP_PASSWORD` | Gmail app password | Required |
| `START_DATE` | Fetch start date (YYYY-MM-DD) | 2025-11-26 |
| `END_DATE` | Fetch end date (YYYY-MM-DD) | 2025-11-28 |
| `OLLAMA_BASE_URL` | Ollama server URL | http://localhost:11434 |
| `OLLAMA_LLM_MODEL` | Ollama LLM model | llama3.1:8b |
| `OLLAMA_EMBEDDING_MODEL` | Ollama embedding model | llama3.1:8b |
| `CHROMA_PERSIST_DIRECTORY` | Vector store location | chroma_store |
| `CHROMA_COLLECTION_NAME` | Collection name | emails |
| `LLM_TEMPERATURE` | LLM temperature | 0.2 |
| `DEFAULT_RETRIEVAL_COUNT` | Results per query | 50 |

## How It Works

### 1. Email Fetching
- Connects to Gmail via IMAP SSL
- Fetches emails within specified date range
- Extracts sender, subject, date, and body
- Decodes email headers properly

### 2. Vector Store Creation
- Cleans email content (removes reply chains)
- Combines metadata with body text
- Generates embeddings using Ollama (llama3.1:8b or nomic-embed-text)
- Stores in ChromaDB with metadata

### 3. Natural Language Query
- Converts user query to embedding via Ollama
- Performs semantic similarity search
- Retrieves top-k relevant emails
- Uses Ollama LLM (llama3.1:8b) to generate natural language response
- Provides accurate, context-aware answers - all locally!

## Examples

### Example Session

```bash
$ python email_assistant.py workflow

============================================================
           EMAIL ASSISTANT - AI-Powered Email Query
============================================================

Running complete workflow: Fetch → Index → Query

Phase 1: Fetching and indexing emails
------------------------------------------------------------
==================================================
EMAIL ASSISTANT - WORKFLOW
==================================================
Email: your-email@gmail.com
Date Range: 2025-11-26 to 2025-11-28
==================================================

Step 1: Fetching emails...
✓ Fetched 15 emails

Step 2: Building ChromaDB vector store...
✓ Vector store created successfully
✓ Total documents in vector store: 15

============================================================
Phase 2: Interactive Query Mode
============================================================

✓ Ready to query 15 emails

Example queries you can try:
  1. How many emails did I receive?
  2. Summarize my emails
  3. Did I receive any important emails?
  4. List all senders

============================================================

Ask a question about your emails (or 'quit' to exit): How many emails did I receive?

Searching and generating response...

Answer: Based on the retrieved emails, you received 15 emails.

------------------------------------------------------------

Ask a question about your emails (or 'quit' to exit): quit

Goodbye!
```

## Troubleshooting

### Authentication Errors

- Ensure 2-Step Verification is enabled
- Use App Password, not regular password
- Check that EMAIL_ID and APP_PASSWORD are correct

### Ollama Connection Issues

- Verify Ollama is running: `ollama list`
- Check OLLAMA_BASE_URL is correct (default: http://localhost:11434)
- Ensure llama3.1:8b model is pulled: `ollama pull llama3.1:8b`
- Test Ollama: `ollama run llama3.1:8b "Hello"`

### Vector Store Not Found

- Run `python email_assistant.py refresh` first
- Check that chroma_store directory exists
- Verify write permissions

### No Emails Found

- Check date range in configuration
- Verify emails exist in that date range
- Try expanding the date range

## Advanced Usage

### Custom Date Ranges

```bash
# Fetch last month's emails
python email_assistant.py refresh --start 2025-10-01 --end 2025-10-31
```

### Programmatic Usage

You can also import and use the modules programmatically:

```python
from config import config
from agent_email_workflow import run_email_workflow
from agent_email_query import load_vector_store, query_emails

# Fetch and index
vectorstore = run_email_workflow()

# Query
response = query_emails(vectorstore, "Summarize my emails")
print(response)
```

## Technical Details

- **LLM**: Ollama (llama3.1:8b) - runs locally
- **Embeddings**: Ollama (llama3.1:8b or nomic-embed-text) - runs locally
- **Vector Database**: ChromaDB
- **Email Protocol**: IMAP4 SSL
- **Email Parsing**: email-reply-parser
- **Framework**: LangChain v0.3+ with Pydantic 2

## Security Notes

- Never commit `.env` file to version control
- Keep your App Password secure
- Rotate API keys periodically
- The `.gitignore` file protects sensitive files

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify your configuration
3. Ensure all dependencies are installed

## Future Enhancements

Potential improvements:
- Support for other email providers
- Web interface
- Email categorization and filtering
- Scheduled email fetching
- Multi-account support
- Export query results
- Email analytics and insights

---

**Happy Querying! 🚀**

