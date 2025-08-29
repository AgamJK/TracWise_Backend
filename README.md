# TracWise Backend

This is the backend for the TracWise project, providing AI-powered Q&A and chat context for tractor maintenance and troubleshooting.

## Features

- AI-powered question answering for tractor-related queries
- Maintains chat context for each session
- REST API for frontend integration
- Gemini AI integration
- Session-based conversation history

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/TracWise_Backend.git
   cd TracWise_Backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file with your API keys and configuration.

### Running the Server

```
python app.py
```

The backend will start on `http://localhost:8000` by default.

## API Endpoints

- `POST /api/qa/`  
  Ask a question. Supports conversation history for context.

  **Request Example:**
  ```json
  {
    "question": "How do I change engine oil?",
    "conversation_history": [
      {"role": "user", "content": "What is engine oil change procedure?"},
      {"role": "assistant", "content": "Here are the steps..."}
    ]
  }
  ```

  **Response Example:**
  ```json
  {
    "answer": "You should change engine oil every 250 hours. Required tools are..."
  }
  ```

## Deployment

You can deploy this backend on Render, Vercel, or any cloud platform that supports Python web servers.

## License

MIT

## Contact

For questions or support, contact [your-email@example.com].
