# UdaPlay Agentic AI — Video Game Research Assistant

UdaPlay is an Agentic AI assistant that answers video game questions with a **state-driven workflow**:

1. Retrieve relevant game context from a local vector store (ChromaDB)
2. Evaluate retrieval quality
3. Fall back to web search (Tavily) when needed
4. Generate a final grounded response and store newly discovered results

It supports both **online mode** (OpenAI + Tavily) and a resilient **offline fallback mode**.

---

## Features

- **Local RAG with ChromaDB** over curated game metadata
- **Agent state machine**: `RETRIEVE → EVALUATE → WEB_SEARCH → FINALIZE`
- **Retrieval quality scoring** with confidence thresholding
- **Web-search fallback** for missing/low-confidence context
- **Long-term memory updates** by upserting new game-like records into Chroma
- **Conversation history awareness** for follow-up questions
- **Offline-safe behavior** when API keys are missing/invalid

---

## Architecture

### Core modules

- `src/main.py` — CLI entry point and app loop
- `src/agent_state.py` — state machine orchestration
- `src/tools.py` — retrieval, evaluation, and web-search utilities
- `src/reporting.py` — response generation and web-result normalization
- `src/vector_store_manager.py` — embeddings + Chroma persistence
- `src/config.py` — environment loading and client initialization

### Runtime flow

```text
User Question
   ↓
RETRIEVE (Chroma query)
   ↓
EVALUATE (confidence + relevance)
   ├── sufficient → FINALIZE (answer from RAG)
   └── insufficient → WEB_SEARCH (Tavily) → upsert → FINALIZE
```

---

## Tech Stack

- Python 3.10+
- ChromaDB (persistent local vector store)
- OpenAI API (embeddings + report/evaluation generation)
- Tavily API (web-search fallback)
- `python-dotenv` for environment configuration

---

## Project Structure

```text
udaplay_agent/
├── data/
│   └── games.json
├── chroma_db/
├── notebooks/
│   ├── Udaplay_01_solution_project.ipynb
│   └── Udaplay_02_solution_project.ipynb
├── src/
│   ├── main.py
│   ├── config.py
│   ├── agent_state.py
│   ├── tools.py
│   ├── reporting.py
│   └── vector_store_manager.py
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
```

Notes:
- If keys are accidentally swapped, runtime logic auto-detects and corrects obvious cases.
- Missing/invalid OpenAI key triggers offline fallback logic.
- Missing/invalid Tavily key disables web search fallback.

### 3) Run the assistant

```bash
python -m src.main
```

Type your question at the prompt:

```text
Ask about a game:
```

Exit with `exit` or `quit`.

---

## Example Questions

- "Tell me about Elden Ring and supported platforms."
- "Who developed Hades?"
- "What are recent updates for Baldur's Gate 3?"
- "Is there a similar game to Hollow Knight?"

---

## Offline Fallback Behavior

When OpenAI is unavailable:
- Embeddings are generated via deterministic local hashing
- Retrieval evaluation uses a heuristic overlap method
- Report generation returns a structured fallback response

This keeps the system functional for local experimentation and demos.

---

## Notebooks

The `notebooks/` folder includes solution notebooks used during project development:

- `Udaplay_01_solution_project.ipynb`
- `Udaplay_02_solution_project.ipynb`

---

## Future Improvements

- Add source-level citation scoring and ranking
- Add richer schema extraction from web results
- Improve memory deduplication for repeated web entries
- Add automated tests for retrieval/evaluation states

---

## License

This project is intended for educational and portfolio use. Add a license file if distributing publicly.
