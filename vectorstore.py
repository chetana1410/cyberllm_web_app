import uuid
import time
from typing import List, Optional, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from embeddings import embed_doc, embed_query

def pinecone_langc_doc(
    index_name: str,
    docs: List[Document],
    namespace: str,
    cloud: str = 'aws',
    region: str = 'us-east-1',
    dimensionality: Optional[int] = 768
) -> None:
    pc = Pinecone(api_key="xxxx")
    spec = ServerlessSpec(cloud=cloud, region=region)

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dimensionality,
            metric="cosine",
            spec=spec
        )
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

    index = pc.Index(index_name)

    texts = [doc.page_content for doc in docs]
    metadata = [doc.metadata for doc in docs]

    doc_embeddings = []
    batch_size = 10
    for i in range(0, len(texts), batch_size):
        text_batch = texts[i:i + batch_size]
        embdds = embed_doc(text_batch)
        doc_embeddings.extend(embdds)
    
    def clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool, list)):
                if isinstance(value, list) and all(isinstance(item, str) for item in value):
                    cleaned_metadata[key] = value
                elif not isinstance(value, list):
                    cleaned_metadata[key] = value
        return cleaned_metadata
    
    vectors = []
    for i, (embedding) in enumerate(doc_embeddings):
        vector = {
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {"text": texts[i], **clean_metadata(metadata[i])}
        }
        vectors.append(vector)
    
    index.upsert(vectors, namespace=namespace)

def query_pinecone(
    index: str,
    query: str,
    namespace: str,
    top_k: int = 4,
    cloud: str = 'aws',
    region: str = 'us-east-1'
) -> List[Dict[str, Any]]:
    pc = Pinecone(api_key="xxxx")
    spec = ServerlessSpec(cloud=cloud, region=region)
    index = pc.Index(index)

    query_embedding = embed_query([query])[0]

    query_response = index.query(
        namespace=namespace,
        top_k=top_k,
        include_metadata=True,
        vector=query_embedding
    )

    results = []
    for match in query_response['matches']:
        result = {
            "id": match['id'],
            "score": match['score'],
            "metadata": match.get('metadata', {})
        }
        results.append(result)
    
    return results
