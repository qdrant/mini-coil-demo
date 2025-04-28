import math
import json


def calculate_avg_length(file_path: str) -> float:
    total_texts_length = 0
    total_texts = 0

    max_docs = 50_000

    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        with open(file_path, "r") as f:
            for line in f:
                data = json.loads(line)
                text = data['title'] + '\n' + data["text"]
                total_texts_length += len(text.strip().split()) 
                total_texts += 1

                if total_texts >= max_docs:
                    break

    return float(math.ceil(total_texts_length / total_texts))