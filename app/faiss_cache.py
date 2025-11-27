import os
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

FAISS_DIR = "vectorstore"

class FaissCache:
    def __init__(self):
        # ✅ Use OpenAI embeddings (latest + correct)
        self.embed = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        self.store = None

        # Load existing FAISS index
        if os.path.exists(f"{FAISS_DIR}/index.faiss"):
            self.store = FAISS.load_local(
                FAISS_DIR,
                self.embed,
                allow_dangerous_deserialization=True
            )

    def search(self, query, threshold=0.3):
        """
        Search for a cached result for a similar query.
        
        Args:
            query: The search query
            threshold: Maximum L2 distance for considering a match
        
        Returns:
            Cached result string if found, None otherwise
        """
        if not self.store:
            return None
        
        # ✅ Check if there's a good match
        if not self.search_with_score(query, threshold):
            return None
            
        docs = self.store.similarity_search(query, k=1)
        if not docs:
            return None

        content = docs[0].page_content
        if not content or "result:" not in content:
            return None

        stored_query, stored_answer = content.split("result:", 1)
        return stored_answer.strip()

    def search_with_score(self, query, threshold=0.3):
        """
        Check if a similar query exists in the cache.
        
        Args:
            query: The search query
            threshold: Maximum L2 distance for a match (lower = more similar)
                      Typical values: 0.1-0.3 for strict matching, 0.3-0.5 for loose
        
        Returns:
            True if a good match is found (score <= threshold), False otherwise
        """
        if not self.store:
            return False

        docs_and_scores = self.store.similarity_search_with_score(query, k=1)
        
        if not docs_and_scores:
            return False
            
        doc, score = docs_and_scores[0]

        # ✅ FIXED: L2 distance → LOWER score = MORE similar
        # For embedding similarity: 0.0 = identical, >0.5 = very different
        if score > threshold:
            print(f"❌ No good match found (distance: {score:.4f} > threshold: {threshold})")
            return False
        
        print(f"✅ Good match found (distance: {score:.4f} <= threshold: {threshold})")
        return True

    def save(self, query, result):
        text = f"query: {query}\nresult: {result}"

        if self.store is None:
            self.store = FAISS.from_texts([text], self.embed)
        else:
            self.store.add_texts([text])

        self.store.save_local(FAISS_DIR)