from pydantic import BaseModel
from typing import List, Any

class QueryRequest(BaseModel):
    question: str
    allow_modifications: bool = False

class QueryResponse(BaseModel):
    sql_query: str
    table: str
    results: List[Any]   
