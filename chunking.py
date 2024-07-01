from unstructured.chunking.title import chunk_by_title

def unstructured_chunk_by_title(elements,max_characters=2000,overlap=200):
    return chunk_by_title(elements,max_characters = max_characters,overlap = overlap)