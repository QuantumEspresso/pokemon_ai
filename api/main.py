from fastapi import FastAPI

app = FastAPI(
    title="Pokémon Champions API",
    description="Read-only API for Pokémon Champions data.",
    version="1.0.0",
)

@app.get("/health", operation_id="health_check")
def health_check():
    return {"status": "ok"}