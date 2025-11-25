import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


FAISS_DIR = "vectorstore"

class FaissCache:
    def __init__(self):
        self.embed = OpenAIEmbeddings()
        self.store = None

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
        if not content:
            return None

        stored_query, stored_answer = content.split("result:", 1)

        return stored_answer.strip()

    def save(self, query, result):
        text = f"query: {query}\nresult: {result}"

        if self.store is None:
            self.store = FAISS.from_texts([text], self.embed)
        else:
            self.store.add_texts([text])

        self.store.save_local(FAISS_DIR)
