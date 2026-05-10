# Final Year Project: Agentic RAG Chatbot

A lightweight document-aware chatbot project built with FastAPI, Streamlit, LangChain, and local MCP tools.

## What this project does

- Hosts a backend chatbot API in `backend_rag.py`.
- Provides a Streamlit frontend UI in `frontend_rag.py`.
- Supports uploading documents and performing Retrieval-Augmented Generation (RAG) over them.
- Uses local MCP servers in `local_mcp_servers/` to extend the agent with:
  - file system operations
  - shell command execution
  - GitHub queries
  - system information

## Project structure

- `backend_rag.py` — FastAPI app with a WebSocket chat endpoint, file upload endpoint, thread management, and RAG support.
- `frontend_rag.py` — Streamlit client that connects to the backend, streams responses, and manages chat threads.
- `local_mcp_servers/` — reusable MCP tool servers launched by the backend:
  - `filesystem_mcp_server.py`
  - `github_mcp_server.py`
  - `shell_mcp_server.py`
  - `system_info_mcp_server.py`
- `database/chatbot.db` — local SQLite checkpoint database used by the chatbot.

## Features

- Document ingestion for PDF, TXT, DOCX, MD, CSV, PPT/PPTX files.
- Chunking and vector embedding using sentence-transformers.
- Semantic similarity search for relevant document snippets.
- WebSocket streaming chat experience.
- Tool-enabled agent capabilities for searching, calculations, file access, GitHub lookups, and system diagnostics.
- Threaded conversations with history and per-thread document context.

## Required environment variables

Create a `.env` file with at least the following keys:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
GITHUB_PAT=your_github_personal_access_token
```

## Setup

1. Install dependencies manually or with your Python environment.

```bash
pip install fastapi uvicorn streamlit langchain langchain-openai langchain-text-splitters langchain-community langchain-mcp-adapters langchain-tavily fastmcp sentence-transformers aiosqlite python-dotenv requests websockets psutil pydantic
```

2. Confirm the `.env` file is present and filled with the required keys.

3. Run the backend API:

```bash
python backend_rag.py
```

4. Run the frontend UI in another terminal:

```bash
streamlit run frontend_rag.py
```

5. Open the Streamlit app in your browser.

## Usage

- Start a new chat thread from the UI.
- Upload one or more documents for the chatbot to use as knowledge context.
- Ask questions about the uploaded files or general queries.
- The backend can use specialized tools to answer with external search, calculations, and file/GitHub access.

## Notes

- The backend launches local MCP tool servers automatically when it starts.
- The frontend expects the backend to be available at `http://localhost:8000`.
- The repo uses `.gitignore` to avoid checking in local files like `.env`, Python caches, and the SQLite database.

## Author

Final year project for BSCS.
