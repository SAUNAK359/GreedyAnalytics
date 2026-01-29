from typing import List


class VectorStore:
    def __init__(self) -> None:
        self._docs = []
        self._embeddings = []
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._index = faiss.IndexFlatL2(384)
        except Exception:
            self._model = None
            self._index = None

    def add_document(self, name: str, text: str) -> None:
        self._docs.append({"name": name, "text": text})
        if self._model and self._index and text:
            vector = self._model.encode([text])
            self._index.add(vector)
            self._embeddings.append(vector)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not self._model or not self._index:
            return [doc["text"] for doc in self._docs[:top_k]]

        vector = self._model.encode([query])
        distances, indices = self._index.search(vector, top_k)
        results = []
        for idx in indices[0]:
            if idx < len(self._docs):
                results.append(self._docs[idx]["text"])
        return results
