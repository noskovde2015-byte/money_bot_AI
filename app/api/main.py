from fastapi import FastAPI
from app.api.lifespan import lifespan
from app.core.config import settings
from app.api.webhook import router as webhook_router
import uvicorn

app = FastAPI(lifespan=lifespan)

app.include_router(webhook_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app", host=settings.run.host, port=settings.run.port, reload=True
    )
