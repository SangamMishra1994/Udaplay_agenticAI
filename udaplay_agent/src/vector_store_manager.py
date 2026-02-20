import os
import json
import hashlib
import chromadb
from .config import openai_client, EMBEDDING_MODEL

class VectorStoreManager:
    def __init__(self, persist_directory=None, collection_name="games"):
        if persist_directory is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_directory = os.path.join(project_root, "chroma_db")

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def embed_text(self, text):
        if openai_client is not None:
            try:
                response = openai_client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=text,
                )
                return response.data[0].embedding
            except Exception:
                pass

        return self.local_embed_text(text)

    def local_embed_text(self, text, dimensions=256):
        values = []
        counter = 0

        while len(values) < dimensions:
            digest = hashlib.sha256(f"{counter}:{text}".encode("utf-8")).digest()
            values.extend([(byte / 255.0) for byte in digest])
            counter += 1

        return values[:dimensions]

    def load_games_from_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def game_to_document(self, game):
        platforms = ", ".join(game.get("platforms", []))
        return (
            f"Title: {game['title']}\n"
            f"Developer: {game['developer']}\n"
            f"Publisher: {game['publisher']}\n"
            f"Release Date: {game['release_date']}\n"
            f"Platforms: {platforms}\n"
            f"Genre: {game['genre']}\n"
            f"Description: {game['description']}"
        )

    def populate_from_games(self, games):
        ids, docs, metas, embeds = [], [], [], []

        for g in games:
            doc = self.game_to_document(g)
            vec = self.embed_text(doc)

            ids.append(g["id"])
            docs.append(doc)
            metas.append(g)
            embeds.append(vec)

        self.collection.upsert(
            ids=ids,
            documents=docs,
            metadatas=metas,
            embeddings=embeds,
        )

    def upsert_game(self, game):
        doc = self.game_to_document(game)
        vec = self.embed_text(doc)

        self.collection.upsert(
            ids=[game["id"]],
            documents=[doc],
            metadatas=[game],
            embeddings=[vec],
        )

    def query(self, query, k=3):
        vec = self.embed_text(query)
        return self.collection.query(
            query_embeddings=[vec],
            n_results=k,
        )
