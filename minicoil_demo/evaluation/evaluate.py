from qdrant_client import QdrantClient, models
import json
import os
from ranx import Qrels, Run, evaluate
import tqdm
import argparse
from minicoil_demo.config import QDRANT_API_KEY, QDRANT_URL, DATA_DIR
from minicoil_demo.model.sparse_vector import query_embedding_to_vector
from minicoil_demo.model.mini_coil import MiniCOIL
from fastembed import SparseTextEmbedding

DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "minicoil.model")

def load_queries(file_path_queries: str, file_path_qrels: str):
    queries = {}

    with open(file_path_queries, "r") as file:
        for line in file:
            row = json.loads(line)
            queries[row["_id"]] = {**row, "doc_ids": []}

    with open(file_path_qrels, "r") as file:
        next(file)
        for line in file:
            query_id, doc_id, score = line.strip().split("\t")
            if int(score) > 0:
                queries[query_id]["doc_ids"].append(doc_id)

    queries_filtered = {}
    for query_id, query in queries.items():
        if len(query["doc_ids"]) > 0:
            queries_filtered[query_id] = query

    return queries_filtered


def main():
    n = 0
    hits = 0
    limit = 10
    #number_of_queries = 100_000

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str)
    parser.add_argument("--input-path-queries", type=str)
    parser.add_argument("--input-path-qrels", type=str)
    parser.add_argument("--collection-name", type=str, default="minicoil-demo")
    parser.add_argument("--total-queries-in-dataset", type=int, default=648)
    parser.add_argument("--ir-datasets-handle", type=str) #https://ir-datasets.com/
    
    args = parser.parse_args()

    model_name = args.model_name or DEFAULT_MODEL_NAME

    queries = load_queries(args.input_path_queries, args.input_path_qrels)

    client = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)

    def search_sparse_minicoil(model: MiniCOIL, query: str, limit: int):
        sparse_vector = query_embedding_to_vector(model, model.encode([query])[0])

        result = client.query_points(
            collection_name=args.collection_name,
            query=sparse_vector,
            using="sparse",
            with_payload=True,
            limit=limit
        )

        return result.points
    
    def search_sparse_bm25(model: SparseTextEmbedding, query, limit):
        sparse_vector_fe = list(model.query_embed(query))[0]

        sparse_vector = models.SparseVector(
            values=sparse_vector_fe.values.tolist(),
            indices=sparse_vector_fe.indices.tolist()
        )

        result = client.query_points(
            collection_name=args.collection_name,
            query=sparse_vector,
            using="sparse",
            with_payload=True,
            limit=limit
        )

        return result.points

    if model_name == 'bm25':
        model = SparseTextEmbedding(
            model_name="Qdrant/bm25"
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
        return

    recalls = []
    precisions = []
    num_queries = 0

    qrels = Qrels.from_ir_datasets(args.ir_datasets_handle)
    run_dict = {}

    for idx, query in tqdm.tqdm(enumerate(queries.values()), total=args.total_queries_in_dataset):
        #if idx >= number_of_queries:
        #    print(f"Processed {number_of_queries} queries, stopping...")
        #    break
        query_dict = {}
        num_queries += 1

        
        if model_name == 'bm25':
            result = search_sparse_bm25(model, query["text"], limit)
        elif model_name == 'minicoil.model':
            result = search_sparse_minicoil(model, query["text"], limit)
        else:
            print(f'''{model_name} is not supported''')
            break
        found_ids = []

        for hit in result:
            found_ids.append(str(hit.id))
            query_dict[str(hit.id)] = hit.score

        query_hits = 0
        for doc_id in query["doc_ids"]:
            n += 1
            if doc_id in found_ids:
                hits += 1
                query_hits += 1

        recalls.append(
            query_hits / len(query["doc_ids"])
        )

        precisions.append(   
            query_hits / limit
        )

        run_dict[query["_id"]] = query_dict

    run = Run(run_dict)
    run.save("run.json")

        #print(f"Processing query: {query}, hits: {query_hits}")

    print(f"Total hits: {hits} out of {n}, which is {hits/n}")

    print(f"Precision: {hits/(num_queries * limit)}")

    average_precision = sum(precisions) / len(precisions)

    print(f"Average precision: {average_precision}")

    average_recall = sum(recalls) / len(recalls)

    print(f"Average recall: {average_recall}")

    print(f'''NDCG@10 by ranx: {evaluate(qrels, run, "ndcg@10")}''')

    print(f'''
        ranx measured hits: {evaluate(qrels, run, "hits")},
        precision@10: {evaluate(qrels, run, "precision@10")},
        recall@10: {evaluate(qrels, run, "recall@10")}
        ''')




if __name__ == "__main__":
    main()