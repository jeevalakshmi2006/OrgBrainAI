"""
ChromaDB wrapper - embedded, persistent, zero external cost.
"""
import chromadb
from config import settings

_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
_collection = _client.get_or_create_collection(name="orgbrain_knowledge")


def add_document(doc_id: str, text: str, metadata: dict):
    _collection.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])


def query(question: str, department_id: str = None, top_k: int = 5):
    where = {"department_id": department_id} if department_id else None
    results = _collection.query(
        query_texts=[question],
        n_results=top_k,
        where=where,
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    output = []
    for doc, meta, dist in zip(docs, metas, dists):
        output.append({"text": doc, "metadata": meta, "distance": dist})
    return output
