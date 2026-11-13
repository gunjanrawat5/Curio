"""Curio API foundation. Provider-backed sessions will be added next."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Curio API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["GET"], allow_headers=["Content-Type"])

@app.get("/health")
def health():
    return {"status": "ok", "mode": "foundation", "evaluation_available": False}

@app.get("/topics")
def topics():
    return [{"id": "fractions_intro", "title": "Fractions", "ages": "8–12", "objectives": ["equal_parts", "same_whole", "more_parts_smaller_parts", "independent_transfer"], "example": ["1/3", "1/4"], "challenge": ["1/6", "1/8"]}]
