from .config import openai_client, CHAT_MODEL


def parse_web_results_to_games(web_results):
    games = []

    for index, result in enumerate(web_results):
        title = result.get("title") or f"Web Result {index + 1}"
        content = result.get("content") or ""
        url = result.get("url") or ""

        game = {
            "id": f"web-{index + 1}",
            "title": title,
            "developer": "Unknown",
            "publisher": "Unknown",
            "release_date": "Unknown",
            "platforms": ["Unknown"],
            "genre": "Unknown",
            "description": content[:500] if content else f"Source: {url}",
        }
        games.append(game)

    return games

def generate_report(question, retrieval_result, evaluation, web_results, new_games, history):
    docs = retrieval_result.get("documents", [[]])[0]
    rag_context = "\n".join(docs)

    if openai_client is None:
        top_doc = docs[0] if docs else "No local context found."
        sources = []
        for result in web_results[:3]:
            url = result.get("url")
            if url:
                sources.append(url)

        if not sources:
            sources.append("local-rag")

        return (
            f"Answer (fallback mode):\n"
            f"Question: {question}\n\n"
            f"Best available context:\n{top_doc}\n\n"
            f"Evaluation: confidence={evaluation.get('confidence')} "
            f"answers_question={evaluation.get('answers_question')}\n"
            f"Sources: {', '.join(sources)}"
        )

    # Build conversation history block
    history_text = ""
    for turn in history[-6:]:  # last 6 messages
        if "user" in turn:
            history_text += f"User: {turn['user']}\n"
        if "assistant" in turn:
            history_text += f"Assistant: {turn['assistant']}\n"

    # Build web citations
    web_context = ""
    for r in web_results:
        title = r.get("title", "")
        url = r.get("url", "")
        snippet = r.get("content", "")[:300]
        web_context += f"[{title}]({url})\n{snippet}\n\n"

    system_prompt = """
    You are UdaPlay, an AI assistant for video game information.
    Use conversation history to resolve pronouns and references.
    Provide clear answers with citations and confidence.
    """

    user_prompt = f"""
    Conversation History:
    {history_text}

    Current Question:
    {question}

    RAG Context:
    {rag_context}

    Web Search Results:
    {web_context}

    Evaluation:
    {evaluation}
    """

    try:
        response = openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content
    except Exception:
        top_doc = docs[0] if docs else "No local context found."
        return (
            f"Answer (fallback mode):\n"
            f"Question: {question}\n\n"
            f"Best available context:\n{top_doc}\n\n"
            f"Evaluation: confidence={evaluation.get('confidence')} "
            f"answers_question={evaluation.get('answers_question')}"
        )
