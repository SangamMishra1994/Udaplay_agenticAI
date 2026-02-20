import os
import sys

try:
    from .vector_store_manager import VectorStoreManager
    from .agent_state import UdaPlayAgent
except ImportError:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from src.vector_store_manager import VectorStoreManager
    from src.agent_state import UdaPlayAgent

def initialize_vector_store():
    vsm = VectorStoreManager()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "games.json")

    games = vsm.load_games_from_json(path)
    vsm.populate_from_games(games)

    return vsm

def main():
    print("🎮 UdaPlay – Video Game Research Agent")
    vsm = initialize_vector_store()
    agent = UdaPlayAgent(vsm)

    while True:
        q = input("Ask about a game: ")
        if q.lower() in ["exit", "quit"]:
            break

        print("\nThinking...\n")
        print(agent.handle_query(q))
        print("\n-----------------------------\n")

if __name__ == "__main__":
    main()
