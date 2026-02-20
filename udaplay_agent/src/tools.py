from .config import openai_client, CHAT_MODEL, tavily_client


def heuristic_evaluate_retrieval(question, docs):
    question_terms = {term for term in question.lower().split() if len(term) > 2}
    best_overlap = 0

    for doc in docs:
        doc_terms = set(doc.lower().split())
        overlap = len(question_terms.intersection(doc_terms))
        best_overlap = max(best_overlap, overlap)

    confidence = min(1.0, best_overlap / max(1, len(question_terms)))
    answers_question = best_overlap > 0

    return {
        "answers_question": answers_question,
        "confidence": round(confidence, 2),
        "use_web_search": not answers_question,
        "reason": "Heuristic fallback evaluation used (OpenAI unavailable).",
    }

def retrieve_game(vsm, question, k=3):
    return vsm.query(question, k)

def evaluate_retrieval(question, retrieved):
    docs = retrieved.get("documents", [[]])[0]

    if not docs:
        return {
            "answers_question": False,
            "confidence": 0.0,
            "use_web_search": True,
            "reason": "No documents found"
        }

    context = "\n".join(docs)

    system_prompt = """
    You evaluate whether retrieved documents answer a video game question.
    Respond in JSON:
    - answers_question (true/false)
    - confidence (0-1)
    - use_web_search (true/false)
    - reason
    """

    user_prompt = f"Question:\n{question}\n\nDocuments:\n{context}"

    if openai_client is None:
        return heuristic_evaluate_retrieval(question, docs)

    try:
        response = openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        import json
        return json.loads(response.choices[0].message.content)
    except Exception:
        return heuristic_evaluate_retrieval(question, docs)

def game_web_search(question):
    if tavily_client is None:
        return []

    try:
        result = tavily_client.search(query=question, max_results=5)
        return result.get("results", [])
    except Exception:
        return []
