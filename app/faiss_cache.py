import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

FAISS_DIR = "vectorstore"

class FaissCache:
    def __init__(self):
        # Use open-source embeddings
        self.embed = SentenceTransformerEmbeddings(
            model_name="BAAI/bge-large-en-v1.5"
        )

        self.store = None

        # Load existing FAISS index
        if os.path.exists(f"{FAISS_DIR}/index.faiss"):
            self.store = FAISS.load_local(
                FAISS_DIR,
                self.embed,
                allow_dangerous_deserialization=True
            )

    def search(self, query):
        if not self.store:
            return None

        docs = self.store.similarity_search(query, k=1)
        if not docs:
            return None

        content = docs[0].page_content
        if not content or "result:" not in content:
            return None

        stored_query, stored_answer = content.split("result:", 1)
        return stored_answer.strip()

    def search_with_score(self, query, threshold=0.5):
        """
        Search for cached results with a similarity score.
        Returns the result if the score is below the threshold (L2 distance).
        """
        if not self.store:
            return None

        # k=1 for best match
        docs_and_scores = self.store.similarity_search_with_score(query, k=1)
        
        if not docs_and_scores:
            return None
            
        doc, score = docs_and_scores[0]
        
        # print(f"DEBUG: Query='{query}' | Score={score} | Threshold={threshold}")

        # For L2 distance, lower is better. 
        # Adjust threshold as needed. 0.0 is exact match.
        if score < threshold:
            return False, score
        
        return True, score

    def save(self, query, result):
        # Store query + result together
        text = f"query: {query}\nresult: {result}"

        if self.store is None:
            self.store = FAISS.from_texts([text], self.embed)
        else:
            self.store.add_texts([text])

        self.store.save_local(FAISS_DIR)
