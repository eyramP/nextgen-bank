from fastapi import FastAPI

app = FastAPI(
    title="Nextgen bank",
    description="Fully featured banking API built with FastAPI",
)

@app.get("/")
def home():
    return {"message": "Welcome to NextGen Banking API"}