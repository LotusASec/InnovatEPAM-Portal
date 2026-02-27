from fastapi import FastAPI

app = FastAPI(title="InnovatEPAM Portal MVP")

@app.get("/health")
def health():
    return {"status": "ok"}
