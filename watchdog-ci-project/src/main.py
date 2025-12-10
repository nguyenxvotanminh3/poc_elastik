from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

# Additional API endpoints can be defined here as needed.