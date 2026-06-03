import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import grafana

app = FastAPI(title="Playwright Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grafana.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8031, reload=True)