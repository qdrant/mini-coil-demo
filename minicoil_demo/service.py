import os

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from minicoil_demo.config import DATA_DIR, ROOT_DIR
from minicoil_demo.model.mini_coil import MiniCOIL

app = FastAPI()

vocab_path = os.path.join(DATA_DIR, "minicoil.model.vocab")
model_path = os.path.join(DATA_DIR, "minicoil.model.npy")

transformer_model = "jinaai/jina-embeddings-v2-small-en-tokens"

mini_coil = MiniCOIL(
    vocab_path=vocab_path,
    word_encoder_path=model_path,
    sentence_encoder_model=transformer_model
)


@app.get("/api/predict")
async def predict(query: str):

    query_empedding = mini_coil.encode([query])[0]

    result = list(query_empedding.values())

    return {
        "result": result
    }

# app.mount("/", StaticFiles(directory=os.path.join(ROOT_DIR, 'frontend', 'dist', 'spa'), html=True))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
