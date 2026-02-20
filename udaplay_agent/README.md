# UdaPlay Agentic AI – Video Game Research Assistant

UdaPlay is an Agentic AI assistant that answers questions about video games using:

- Local RAG (ChromaDB)
- Web search fallback (Tavily)
- Retrieval evaluation
- Long‑term memory updates
- Structured reporting

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Create a `.env` file in the project root:

   OPENAI_API_KEY="your-openai-key"
   TAVILY_API_KEY="your-tavily-key"

3. Run the agent:
   python -m src.main
