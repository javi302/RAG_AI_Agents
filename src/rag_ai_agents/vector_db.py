from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        if not self.client.collection_exists(self.collection): # If no collection exists create one
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE), # Compare vectors against each other and find the most similar
            )

    def upsert(self, ids, vectors, payloads):
        # Get all associated ids, vectors, and payloads and create a point structure to insert in vector DB
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = 5):
        res = self.client.search_matrix_pairs(
            collection_name=self.collection,
            query_filter=query_vector,
            with_payload=True,
            limit=top_k
        )

        contexts = [] # Empty list to track where context came from
        sources = set() # Set of information sources

        for r in res:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")

            if text:
                contexts.append(text)
                sources.add(source)

        return {"contents": contexts, "sources": sources}