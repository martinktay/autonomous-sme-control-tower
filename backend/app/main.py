from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import invoices, signals, memory, stability, strategy, actions, voice, orchestration

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Autonomous operations platform for SMEs",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invoices.router)
app.include_router(signals.router)
app.include_router(memory.router)
app.include_router(stability.router)
app.include_router(strategy.router)
app.include_router(actions.router)
app.include_router(voice.router)
app.include_router(orchestration.router)


@app.get("/")
async def root():
    return {
        "message": "Autonomous SME Control Tower API",
        "status": "operational"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
