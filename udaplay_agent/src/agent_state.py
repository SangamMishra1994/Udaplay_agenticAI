from .tools import retrieve_game, evaluate_retrieval, game_web_search
from .reporting import generate_report, parse_web_results_to_games

class UdaPlayAgent:
    def __init__(self, vsm, confidence_threshold=0.6):
        self.vsm = vsm
        self.confidence_threshold = confidence_threshold
        
        # Conversation history
        self.history = []   # list of {"user": "...", "assistant": "..."}
        
        # State machine definition
        self.state = "RETRIEVE"
        self.next_state = {
            "RETRIEVE": "EVALUATE",
            "EVALUATE": "WEB_SEARCH",
            "WEB_SEARCH": "FINALIZE",
            "FINALIZE": None
        }

    def handle_query(self, question):
        # Add user message to history
        self.history.append({"user": question})
        
        # STATE 1: RETRIEVE
        self.state = "RETRIEVE"
        rag = retrieve_game(self.vsm, question)
        
        # STATE 2: EVALUATE
        self.state = "EVALUATE"
        evaluation = evaluate_retrieval(question, rag)
        
        use_rag = evaluation["answers_question"] and evaluation["confidence"] >= self.confidence_threshold
        
        web_results = []
        new_games = []
        
        # STATE 3: WEB_SEARCH (fallback)
        if not use_rag or evaluation["use_web_search"]:
            self.state = "WEB_SEARCH"
            web_results = game_web_search(question)
            new_games = parse_web_results_to_games(web_results)
            
            for g in new_games:
                self.vsm.upsert_game(g)
        
        # STATE 4: FINALIZE
        self.state = "FINALIZE"
        answer = generate_report(
            question=question,
            retrieval_result=rag,
            evaluation=evaluation,
            web_results=web_results,
            new_games=new_games,
            history=self.history
        )
        
        # Add assistant response to history
        self.history.append({"assistant": answer})
        
        return answer
