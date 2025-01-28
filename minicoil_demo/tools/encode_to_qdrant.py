import argparse

import os
import json
from typing import Dict, Iterable, Tuple

from qdrant_client import QdrantClient, models

import tqdm
from minicoil_demo.config import DATA_DIR, QDRANT_API_KEY, QDRANT_URL
from minicoil_demo.model.mini_coil import MiniCOIL, WordEmbedding
from minicoil_demo.model.sparse_vector import SparseVectorConverter

DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "minicoil.model")


def read_file(file_path) -> Iterable[Tuple[int, str]]:
    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        with open(file_path, "r") as f:
            for idx, line in enumerate(f):
                data = json.loads(line)
                yield int(data.get("_id", idx)), data["text"]
    else:
        with open(file_path, "r") as f:
            for idx, line in enumerate(f):
                yield idx, line.strip()


def embedding_stream(model: MiniCOIL, file_path, parallel = None) -> Iterable[Dict[str, WordEmbedding]]:
    stream = map(lambda x: x[1], read_file(file_path))
    for sentence_embeddings in model.encode_steam(stream, parallel=parallel):
        yield sentence_embeddings


def read_points(model: MiniCOIL, file_path: str, parallel: int = 4) -> Iterable[models.PointStruct]:
    converted = SparseVectorConverter()
    sentences = read_file(file_path)
    embeddings = embedding_stream(model, file_path=file_path, parallel=parallel)
    sparse_vectors = map(lambda x: converted.embedding_to_vector(model, x), embeddings)
    
    for (idx, sentence), sparse_vector in zip(sentences, sparse_vectors):
        yield models.PointStruct(
            id=idx,
            vector={
                "minicoil": sparse_vector,
            },
            payload={
                "sentence": sentence
            }
        )
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str)
    parser.add_argument("--input-path", type=str)
    parser.add_argument("--collection-name", type=str, default="minicoil-demo")
    parser.add_argument("--parallel", type=int, default=4)
    
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

    qdrant_cleint = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True
    )
    
    if qdrant_cleint.collection_exists(args.collection_name):
        print(f"Collection {args.collection_name} already exists. Deleting...")
        qdrant_cleint.delete_collection(args.collection_name)

    qdrant_cleint.create_collection(
        collection_name=args.collection_name,
        vectors_config={},
        sparse_vectors_config={
            "minicoil": models.SparseVectorParams(
                index=models.SparseIndexParams(
                    on_disk=True
                ),
                modifier=models.Modifier.IDF,
            )
        }
    )
        
    import ipdb
    with ipdb.launch_ipdb_on_exception():
        qdrant_cleint.upload_points(
            collection_name=args.collection_name,
            points=tqdm.tqdm(read_points(mini_coil, args.input_path, parallel=args.parallel)),
            batch_size=32
        )


if __name__ == '__main__':
    main()
