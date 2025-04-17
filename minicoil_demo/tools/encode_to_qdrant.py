import argparse

import os
import math
import json
from typing import Dict, Iterable, Tuple

from qdrant_client import QdrantClient, models

import tqdm
from minicoil_demo.config import DATA_DIR, QDRANT_API_KEY, QDRANT_URL
from minicoil_demo.model.mini_coil import MiniCOIL, WordEmbedding
from minicoil_demo.model.sparse_vector import SparseVectorConverter

DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "minicoil.model")

def calculate_avg_length(file_path: str) -> float:
    total_texts_length = 0
    total_texts = 0

    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        with open(file_path, "r") as f:
            for line in f:
                data = json.loads(line)
                text = data['title'] + '\n' + data["text"]
                total_texts_length += len(text.strip().split()) 
                total_texts += 1

    return float(math.ceil(total_texts_length / total_texts))


def read_file(file_path, skip_first = 0) -> Iterable[Tuple[int, str]]:
    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        with open(file_path, "r") as f:
            for idx, line in enumerate(f):
                if idx < skip_first:
                    continue
                data = json.loads(line)
                yield idx, data["_id"], data["title"], data["text"]


def embedding_stream(model: MiniCOIL, file_path, skip_first = 0, parallel = None) -> Iterable[Dict[str, WordEmbedding]]:
    stream = map(lambda x: x[2] + '\n' + x[3], read_file(file_path, skip_first=skip_first)) # https://github.com/castorini/anserini/blob/4de1d53629507eb9051300a38d46cbc460b4e7d9/src/main/java/io/anserini/collection/BeirFlatCollection.java#L77
    for sentence_embeddings in model.encode_steam(stream, parallel=parallel):
        yield sentence_embeddings


def read_points(
        model: MiniCOIL,
        file_path: str,
        parallel: int = 4,
        skip_first: int = 0,
        avg_len: float = 150.0
) -> Iterable[models.PointStruct]:
    converted = SparseVectorConverter(avg_len=avg_len) #https://arxiv.org/pdf/2307.10488
    sentences = read_file(file_path, skip_first=skip_first)

    embeddings = embedding_stream(model, file_path=file_path, skip_first=skip_first, parallel=parallel)
    sparse_vectors = map(lambda x: converted.embedding_to_vector(model, x), embeddings)
    
    for (idx, sentence_id, title, text), sparse_vector in zip(sentences, sparse_vectors):
        yield models.PointStruct(
            id=idx,
            vector={
                "minicoil": sparse_vector,
            },
            payload={
                "sentence": title + '\n' + text,
                "sentence_id": sentence_id,
            }
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str)
    parser.add_argument("--input-path", type=str) # Path to the corpus.jsonl of BEIR dataset
    parser.add_argument("--collection-name", type=str, default="minicoil-demo")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--skip-first", type=int, default=0)
    
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

    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True
    )

    if args.skip_first == 0:
        if qdrant_client.collection_exists(args.collection_name):
            print(f"Collection {args.collection_name} already exists. Deleting...")
            qdrant_client.delete_collection(args.collection_name)

        qdrant_client.create_collection(
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

    print("Calculating average length of the dataset") #needed only for BEIR benchmarks, in our implementation of BM25/miniCOIL avg_len needs to be provided by the user
    avg_len = calculate_avg_length(args.input_path)
    print(f"Calculated average length: {avg_len}")

    points_iterator = read_points(mini_coil, args.input_path, parallel=args.parallel, skip_first=args.skip_first, avg_len=avg_len)

    import ipdb
    with ipdb.launch_ipdb_on_exception():
        qdrant_client.upload_points(
            collection_name=args.collection_name,
            points=tqdm.tqdm(points_iterator),
            batch_size=32
        )


if __name__ == '__main__':
    main()
