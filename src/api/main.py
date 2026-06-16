from fastapi import FastAPI
from .router import router as api_router

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
