
from typing import List
from minicoil_demo.model.mini_coil import MiniCOIL

from qdrant_client import models


def normalize_vector(vector: List[float]) -> List[float]:
    norm = sum([x ** 2 for x in vector]) ** 0.5
    return [x / norm for x in vector]


def embedding_to_vector(model: MiniCOIL, sentence_embedding: List[dict]) -> models.SparseVector:
    indicies = []
    values = []
    
    embedding_size = model.output_dim
    
    for embedding in sentence_embedding.values():
        word_id = embedding["word_id"]
        
        if word_id >= 0:
            embedding = embedding["embedding"]
            normalized_embedding = normalize_vector(embedding)
            for val_id, value in enumerate(normalized_embedding):
                indicies.append(word_id * embedding_size + val_id)
                values.append(value)
    
    return models.SparseVector(
        indices=indicies,
        values=values,
    )
