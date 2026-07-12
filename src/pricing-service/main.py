from fastapi import FastAPI

from pricing_engine import PricingEngine
from utils import get_logger

logger = get_logger("PricingServiceMain")


app = FastAPI(
    title="Pricing Service",
    description="Real-time surge pricing engine for ride-sharing platform.",
    version="1.0.0",
)


engine = PricingEngine()
SURGE_CACHE = {}


# ----------------------------
# Startup Sequence
# ----------------------------


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Pricing Service...")
    logger.info("Pricing Service started successfully.")


# ----------------------------
# Health Check Endpoint
# ----------------------------


@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "service": "pricing-service",
        "surge_cache_size": len(SURGE_CACHE),
    }


# ----------------------------
# Manual run for local usage
# ----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
