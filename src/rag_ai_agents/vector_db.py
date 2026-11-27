"""------------------------------------------------------------------------------------------------------
# Qdrant class to that connects system to the server, ingests PDFs, if similar content exists the
# current ID will be overwritten, and takes a query question that returns relevant chunks of information
# Inngest: PDF -> chunks of text -> embedding model -> vectors -> upsert() -> qdrant
# Query: question -> embedding model -> query vector -> search() -> top chuncks
#        -> chunks are passed to the LLM for context of its answer 
#--------------------------------------------------------------------------------------------------------
"""

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=3072):
        self.client = QdrantClient(url=url, timeout=30) # Connect to qdrant server at given URL 
        self.collection = collection # 
        if not self.client.collection_exists(self.collection): # If no collection exists create one, allows safe storage without wiping data
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=dim, # Embeddings model's size (must match exactly)
                    distance=Distance.COSINE # Compare vectors against each other (find most similar meaning)
                    ), 
            )

    def upsert(self, ids, vectors, payloads):
        # Get all associated ids, vectors, and payloads and create a point structure to insert in vector DB during inngest
        # One chunk: ids (qdrant accepts ints or UUID), vector (chunk's embeddings), payloads (metadata kept with vector)
        # PointStruct bundles the three values into one record qdrant can store 
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        # "upsert:" update if ID exists, else insert
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = 5):
        # Called once user query is entered
        res = self.client.query_points(
            collection_name=self.collection,
            query_vector=query_vector,
            with_payload=True,
            limit=top_k
        ).points

        contexts = [] # Empty list to store chunks in ranked order to pass to LLM
        sources = set() # Unique sources files (set to drop duplicate chunks from same file)

        for r in res:
            # Each chunk has .id, .score (similarity), .payload (metadata), {} to protect against hit with no payload
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")

            if text: # Skip empty chunks
                contexts.append(text)
                sources.add(source)

        return {"contents": contexts, "sources": list(sources)}