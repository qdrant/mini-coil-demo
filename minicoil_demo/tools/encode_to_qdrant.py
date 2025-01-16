import argparse

import os
from typing import Iterable
import uuid
import json

from qdrant_client import QdrantClient, models

import tqdm
from minicoil_demo.config import DATA_DIR, QDRANT_API_KEY, QDRANT_URL
from minicoil_demo.model.mini_coil import MiniCOIL
from minicoil_demo.model.sparse_vector import embedding_to_vector

from fastembed import SparseTextEmbedding

DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "minicoil.model")


def read_file(file_path: str):
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()


def read_file_beir(file_path: str) -> Iterable[str]:
    with open(file_path, "r") as file:
        for line in file:
            row = json.loads(line)
            yield row["_id"], row["text"]

def read_texts_beir(file_path: str) -> Iterable[str]:
    with open(file_path, "r") as file:
        for line in file:
            row = json.loads(line)
            yield row["text"]

def embedding_stream(model: MiniCOIL, file_path: str) -> Iterable[dict]:
    stream = read_file(file_path)
    for sentence_embeddings in model.encode_steam(stream, parallel=4):
        yield sentence_embeddings


def embedding_stream_beir(model: MiniCOIL, file_path: str) -> Iterable[dict]:
    stream = read_texts_beir(file_path)
    for sentence_embeddings in model.encode_steam(stream, parallel=4):
        yield sentence_embeddings


def read_points(model: MiniCOIL, file_path: str):
    sentences = read_file(file_path)
    embeddings = embedding_stream(model, file_path=file_path)
    sparse_vectors = map(lambda x: embedding_to_vector(model, x), embeddings)
    
    for sentence, sparse_vector in zip(sentences, sparse_vectors):
        yield models.PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "minicoil": sparse_vector,
            },
            payload={
                "sentence": sentence
            }
        )


def read_points_beir(model: MiniCOIL, file_path: str, total_points: int = 523000) -> Iterable[models.PointStruct]:
    embeddings = embedding_stream_beir(model, file_path=file_path)
    sparse_vectors = map(lambda x: embedding_to_vector(model, x), embeddings)
    
    for ((id_text, text), sparse_vector) in tqdm.tqdm(zip(read_file_beir(file_path), sparse_vectors), total=total_points, desc="Processing points, BEIR"): #quora
        yield models.PointStruct(
            id=int(id_text),
            vector={
                "minicoil": sparse_vector,
            },
            payload={
                "sentence": text
            }
        )

def read_points_beir_bm25(model: SparseTextEmbedding, file_path: str, total_points: int = 523000) -> Iterable[models.PointStruct]:
    for ((id_text, text), embedding) in zip(read_file_beir(file_path), model.embed(tqdm.tqdm(read_texts_beir(file_path), total=total_points, desc="Processing points, BEIR"), batch_size=32)):
        yield models.PointStruct(
            id=int(id_text),
            vector={
                "bm25": models.SparseVector(
                    values=embedding.values.tolist(),
                    indices=embedding.indices.tolist()
                )
            },
            payload={
                "sentence": text
            }
        )
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str)
    parser.add_argument("--input-path", type=str)
    parser.add_argument("--is-beir-dataset", action="store_true")
    parser.add_argument("--collection-name", type=str, default="minicoil-demo")
    
    args = parser.parse_args()

    model_name = args.model_name or DEFAULT_MODEL_NAME

    if model_name == 'bm25':
        model = SparseTextEmbedding(
            model_name="Qdrant/bm25",
            avg_len=6.0 #if DATASET == "quora" else 256.,
        )
    elif model_name == 'minicoil.model':
        vocab_path = os.path.join(DATA_DIR, f"{model_name}.vocab")
        model_path = os.path.join(DATA_DIR, f"{model_name}.npy")
        transformer_model = "jinaai/jina-embeddings-v2-small-en-tokens"
        model = MiniCOIL(
            vocab_path=vocab_path,
            word_encoder_path=model_path,
            sentence_encoder_model=transformer_model
        )
    else:
        print(f'''{model_name} is not supported''')

    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    
    if model_name == 'bm25':
        if not qdrant_client.collection_exists(args.collection_name):
            qdrant_client.create_collection(
                collection_name=args.collection_name,
                vectors_config={},
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams()
                }
            )
    elif model_name == 'minicoil.model':
        if not qdrant_client.collection_exists(args.collection_name):
            qdrant_client.create_collection(
                collection_name=args.collection_name,
                vectors_config={},
                sparse_vectors_config={
                    "minicoil": models.SparseVectorParams()
                }
            )
    else:
        print(f'''{model_name} is not supported''')
        
    import ipdb

    if args.is_beir_dataset:
        if model_name == 'bm25':
            with ipdb.launch_ipdb_on_exception():
                qdrant_client.upload_points(
                    collection_name=args.collection_name,
                    points=tqdm.tqdm(read_points_beir_bm25(model, args.input_path))
                )
        elif model_name == "minicoil.model":  
            with ipdb.launch_ipdb_on_exception():
                qdrant_client.upload_points(
                    collection_name=args.collection_name,
                    points=tqdm.tqdm(read_points_beir(model, args.input_path))
                )
        else:
            print(f'''{model_name} is not supported''')
    else:
        with ipdb.launch_ipdb_on_exception():
            qdrant_client.upload_points(
                collection_name=args.collection_name,
                points=tqdm.tqdm(read_points(model, args.input_path))
            )


if __name__ == '__main__':
    main()
