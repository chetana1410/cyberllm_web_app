from typing import List, Optional
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

def embed_doc(
    texts: List[str],
    task: str = "RETRIEVAL_DOCUMENT",
    model_name: str = "text-embedding-004",
    dimensionality: Optional[int] = 768,
) -> List[List[float]]:
    model = TextEmbeddingModel.from_pretrained(model_name)
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)
    return [embedding.values for embedding in embeddings]

def embed_query(
    texts: List[str],
    task: str = "RETRIEVAL_QUERY",
    model_name: str = "text-embedding-004",
    dimensionality: Optional[int] = 768,
) -> List[List[float]]:
    model = TextEmbeddingModel.from_pretrained(model_name)
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)
    return [embedding.values for embedding in embeddings]
