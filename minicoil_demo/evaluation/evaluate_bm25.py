from qdrant_client import QdrantClient, models
import json
import os
from ranx import Qrels, Run, evaluate
import tqdm
import argparse
from minicoil_demo.config import QDRANT_API_KEY, QDRANT_URL, DATA_DIR
from fastembed import SparseTextEmbedding

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
    parser.add_argument("--input-path-queries", type=str)
    parser.add_argument("--input-path-qrels", type=str)
    parser.add_argument("--collection-name", type=str, default="bm25")

    args = parser.parse_args()

    queries = load_queries(args.input_path_queries)
    qrels = load_qrels(args.input_path_qrels)

    client = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)

    def search_sparse_bm25(model: SparseTextEmbedding, query: str, limit: int):
        sparse_vector_fe = list(model.query_embed(query))[0]
        sparse_vector = models.SparseVector(
            values=sparse_vector_fe.values.tolist(), indices=sparse_vector_fe.indices.tolist()
        )

        result = client.query_points(
            collection_name=args.collection_name,
            query=sparse_vector,
            using="bm25",
            with_payload=True,
            limit=limit
        )

        return result.points


    model = SparseTextEmbedding(model_name="Qdrant/bm25") #also here k, b, avg_len  shouldn't be important for query_embed.

    run_dict = {}

    for query_id in tqdm.tqdm(qrels):
        query_dict = {}

        result = search_sparse_bm25(model, queries[query_id]["text"], limit)
        
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
