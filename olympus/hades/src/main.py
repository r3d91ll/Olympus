from fastapi import FastAPI
from loguru import logger
import uvicorn

from api.router import router as api_router
from core.config import settings
from core.monitoring import init_monitoring

app = FastAPI(
    title="HADES API",
    description="Heuristic Adaptive Data Extraction System",
    version="1.0.0"
)

# Initialize monitoring
init_monitoring(app)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting HADES API server...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down HADES API server...")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
