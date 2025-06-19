import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.get("/")
async def home():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("web-service:app", host="0.0.0.0", port=8000)