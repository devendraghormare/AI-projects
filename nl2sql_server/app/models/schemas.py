from pydantic import BaseModel
from typing import List, Any, Optional, Dict 

class QueryRequest(BaseModel):
    question: str
    allow_modifications: bool = False

class QueryResponse(BaseModel):
    sql_query: str
    table: str
    results: List[Any]
    token_usage: Optional[Dict[str, int]] = None 
