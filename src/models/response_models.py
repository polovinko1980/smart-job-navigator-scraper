from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel

class JobDetails(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    rawJobDescription: Optional[str] = None
    companyName: Optional[str] = None
    position: Optional[str] = None

class SearchResults(BaseModel):
    urls: Optional[List[Optional[str]]] = None

class DetailsResults(BaseModel):
    jobDetails: Optional[List[Optional[JobDetails]]] = None

class ScraperResponsePayload(BaseModel):
    response: Optional[str] = None
