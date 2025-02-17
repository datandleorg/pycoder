from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import uuid
import json

class QdrantService:
    def __init__(self, host='localhost', port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.nlp_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.code_model = SentenceTransformer('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)
        self.code_model.max_seq_length = 8192  # Increase context length if needed

    def create_collection(self, collection_name):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "text": VectorParams(size=384, distance=Distance.COSINE),
                "code": VectorParams(size=768, distance=Distance.COSINE),
            }
        )

    def insert_code_snippet(self, collection_name, code_snippet, metadata):
        text_representation = self._textify(metadata)
        text_embedding = self.nlp_model.encode(text_representation).tolist()
        code_embedding = self.code_model.encode(code_snippet).tolist()
        point = PointStruct(
            id=uuid.uuid4().hex,
            vector={"text": text_embedding, "code": code_embedding},
            payload=metadata
        )
        self.client.upsert(collection_name=collection_name, points=[point])

    def search(self, collection_name, query, top_k=10):
        query_embedding = self.nlp_model.encode(query).tolist()
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            search_params={"using": "text"},
            limit=top_k,
            with_payload=True
        )
        return results

    def _textify(self, metadata):
        # Convert metadata into a human-readable text representation
        components = [metadata.get(key, '') for key in ['name', 'signature', 'docstring', 'module', 'struct_name']]
        return ' '.join(components)

# Example usage
if __name__ == "__main__":
    qdrant_service = QdrantService()
    qdrant_service.create_collection("codebase_collection")

    # Example code snippet and metadata
    code_snippet = """
    /// Return `true` if ready, `false` if timed out.
    pub fn await_ready_for_timeout(&self, timeout: Duration) -> bool {
        let mut is_ready = self.value.lock();
        if !*is_ready {
            !self.condvar.wait_for(&mut is_ready, timeout).timed_out()
        } else {
            true
        }
    }
    """
    metadata = {
        "name": "await_ready_for_timeout",
        "signature": "fn await_ready_for_timeout(&self, timeout: Duration) -> bool",
        "docstring": "Return `true` if ready, `false` if timed out.",
        "module": "common",
        "file_path": "lib/collection/src/common/is_ready.rs",
        "struct_name": "IsReady"
    }

    qdrant_service.insert_code_snippet("codebase_collection", code_snippet, metadata)
    results = qdrant_service.search("codebase_collection", query="function to check readiness with timeout")
    for result in results:
        print(result.payload)
