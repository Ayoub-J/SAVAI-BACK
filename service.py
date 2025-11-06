# service.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from telecom_analyzer import analyze_tweets

app = FastAPI(title="Telecom Tweet Analyzer")

class AnalyzeRequest(BaseModel):
    tweets: List[str]

class AnalyzeResponseItem(BaseModel):
    tweet: str
    sentiment: str
    thème: str
    urgence: int

@app.post("/analyze", response_model=List[AnalyzeResponseItem])
def analyze(req: AnalyzeRequest):
    return analyze_tweets(req.tweets)
