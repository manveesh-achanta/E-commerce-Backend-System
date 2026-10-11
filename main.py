from fastapi import FastAPI
from models import Base
from database import engine
from contextlib import asynccontextmanager
from api.customers import customer_router
from api.seller import seller_router
from api.products import product_router


@asynccontextmanager
async def lifespan(app : FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(customer_router)
app.include_router(seller_router)
app.include_router(product_router)


@app.get("/status")
async def check_status():
    return {"Message" : "Running"}