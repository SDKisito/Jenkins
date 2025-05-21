from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Application Examen Jenkins pour Saliou DIEDHIOU"}
