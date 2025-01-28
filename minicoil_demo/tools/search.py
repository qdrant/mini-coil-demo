import argparse
import os

from qdrant_client import QdrantClient, models

from minicoil_demo.config import DATA_DIR, QDRANT_API_KEY, QDRANT_URL
from minicoil_demo.model.mini_coil import MiniCOIL
from minicoil_demo.model.sparse_vector import SparseVectorConverter


DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "minicoil.model")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str)
    parser.add_argument("--model-name", type=str)
    parser.add_argument("--collection-name", type=str, default="minicoil-demo")
    
    args = parser.parse_args()

    model_name = args.model_name or DEFAULT_MODEL_NAME
    vocab_path = os.path.join(DATA_DIR, f"{model_name}.vocab")
    model_path = os.path.join(DATA_DIR, f"{model_name}.npy")

    transformer_model = "jinaai/jina-embeddings-v2-small-en-tokens"

    mini_coil = MiniCOIL(
        vocab_path=vocab_path,
        word_encoder_path=model_path,
        sentence_encoder_model=transformer_model
    )
    
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    converter = SparseVectorConverter()
    
    embeddings = mini_coil.encode([args.query])[0]

    print(f"Embeddings: {embeddings}")
    
    sparse_vector = converter.embedding_to_vector_query(mini_coil, embeddings)
    
    print(f"Query: {args.query}")
    print(f"Sparse Vector: {sparse_vector}")
    
    response = client.query_points(
        collection_name=args.collection_name,
        query=sparse_vector,
        using="minicoil",
        limit=5
    )
    
    for point in response.points:
        print(f"Point: {point.payload['sentence']}")
    

if __name__ == '__main__':
    main()