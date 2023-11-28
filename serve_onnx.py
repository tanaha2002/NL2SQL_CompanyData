from fastapi import FastAPI
from fastapi.responses import JSONResponse
from modules.sentence_embbeding import SentenceEmbedding
from fastapi import HTTPException
from pydantic import BaseModel
import torch
onnx_path = './modules/embeddings.onnx'
tokenizer_path = './tokenizer'
app = FastAPI()


@app.get("/")
def check_health():
    return {"status": "OK"}

@app.post("/init/")
def init():
    try:
        global sentence_embedding
        sentence_embedding = SentenceEmbedding(tokenizer_path, onnx_path)
        sample = 'Tiên nhân khắc khoải đợi chờ, Phàm nhân thư thả sống đời an nhiên.'
        print(type(sample))
        embe = sentence_embedding.embed(sample)
        print(embe)
        print("Success sample")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize sentence_embedding"
        )
    return {"status": "OK"}

@app.post("/result")
def result(text: str):
    print(text)
    embedding = sentence_embedding.embed(text)
    #convert numpy.ndarray to list but still keep  precision of floating-point numbers
    list_from_numpy = lambda x: [float(i) for i in x]
    embedding_ = list_from_numpy(embedding)
    print(f"embedding in API: {embedding}")

    return {
        'embedding': embedding_,
    }