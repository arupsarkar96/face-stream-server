
from pydantic import BaseModel
from typing import List

class ResultItem(BaseModel):
    person_id: str
    similarity: float

class FaissSearchResult(BaseModel):
    matches: List[ResultItem]
    search_time_ms: int
    entries_searched: int
