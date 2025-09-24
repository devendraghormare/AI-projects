
from fastapi import FastAPI, HTTPException
from api.v1.endpoints import query
from core.logger import setup_logging

setup_logging()

app = FastAPI(
    title="NL2SQL Server",
    description="Convert Natural Language to SQL Queries",
    version="1.0.0"
)

app.include_router(query.router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "NL2SQL Server Running!"}