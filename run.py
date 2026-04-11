"""Punto di ingresso per avviare AtlasPI in locale."""

import uvicorn

from src.config import HOST, PORT, RELOAD

if __name__ == "__main__":
    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=RELOAD)
