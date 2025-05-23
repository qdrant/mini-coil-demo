from qdrant_client import QdrantClient
import json
import os
from ranx import Qrels, Run, evaluate
import tqdm
import argparse
from minicoil_demo.config import QDRANT_API_KEY, QDRANT_URL, DATA_DIR
from minicoil_demo.model.sparse_vector import SparseVectorConverter
from minicoil_demo.model.mini_coil import MiniCOIL

DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "minicoil.model")

def load_qrels(file_path_qrels: str):
    qrels = {}

    with open(file_path_qrels, "r") as file:
        next(file) #header
        for line in file:
            query_id, doc_id, score = line.strip().split("\t")
            if int(score) > 0:
                if query_id not in qrels:
                    qrels[query_id] = {}
                qrels[query_id][doc_id] = int(score)

    return qrels

def load_queries(file_path_queries: str):
    queries = {}

    with open(file_path_queries, "r") as file:
        for line in file:
            row = json.loads(line)
            queries[row["_id"]] = {**row}

    return queries


def main():
    limit = 10

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str)
    parser.add_argument("--input-path-queries", type=str)
    parser.add_argument("--input-path-qrels", type=str)
    parser.add_argument("--collection-name", type=str, default="minicoil-demo")

    args = parser.parse_args()

    model_name = args.model_name or DEFAULT_MODEL_NAME

    queries = load_queries(args.input_path_queries)
    qrels = load_qrels(args.input_path_qrels)

    client = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)

    converter = SparseVectorConverter() #k, b, avg_len don't affect query embeddings

    def search_sparse_minicoil(model: MiniCOIL, query: str, limit: int):
        embedding = model.encode([query])[0]
        sparse_vector = converter.embedding_to_vector_query(model, embedding)

        result = client.query_points(
            collection_name=args.collection_name,
            query=sparse_vector,
            using="minicoil",
            with_payload=True,
            limit=limit
        )

        return result.points

    vocab_path = os.path.join(DATA_DIR, f"{model_name}.vocab")
    model_path = os.path.join(DATA_DIR, f"{model_name}.npy")
    transformer_model = "jinaai/jina-embeddings-v2-small-en-tokens"

    model = MiniCOIL(
        vocab_path=vocab_path,
        word_encoder_path=model_path,
        sentence_encoder_model=transformer_model
    )

    run_dict = {}

    for query_id in tqdm.tqdm(qrels):
        query_dict = {}

        result = search_sparse_minicoil(model, queries[query_id]["text"], limit)
        
        for hit in result:
            query_dict[hit.payload["sentence_id"]] = hit.score #"sentence_id" for consistency with encode_to_qdrant

        run_dict[query_id] = query_dict

    run = Run(run_dict)
    qrels = Qrels(qrels)

    print(f'''NDCG@10: {evaluate(qrels, run, "ndcg@10")}''')
    print(f'''
        precision@10: {evaluate(qrels, run, "precision@10")},
        recall@10: {evaluate(qrels, run, "recall@10")}
        ''')


if __name__ == "__main__":
    main()
