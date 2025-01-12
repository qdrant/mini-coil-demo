import os

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from minicoil_demo.config import DATA_DIR, ROOT_DIR
from minicoil_demo.model.mini_coil import MiniCOIL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_name = os.getenv("MODEL_NAME", "minicoil.model")

vocab_path = os.path.join(DATA_DIR, f"{model_name}.vocab")
model_path = os.path.join(DATA_DIR, f"{model_name}.npy")

transformer_model = "jinaai/jina-embeddings-v2-small-en-tokens"

mini_coil = MiniCOIL(
    vocab_path=vocab_path,
    word_encoder_path=model_path,
    sentence_encoder_model=transformer_model
)


@app.get("/api/embed")
async def embed(query: str):

    query_empedding = mini_coil.encode([query])[0]

    result = list(query_empedding.values())

    return {
        "result": result
    }

app.mount("/", StaticFiles(directory=os.path.join(ROOT_DIR, 'frontend', 'dist'), html=True))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
