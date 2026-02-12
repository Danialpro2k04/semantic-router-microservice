import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient


COLLECTION_NAME = "enterprise_router"
QDRANT_URL = "http://localhost:6333"
CONFIDENCE_THRESHOLD = 0.82  #Strict threshold for enterprise accuracy


app = FastAPI(title="Semantic Router Microservice")
client = QdrantClient(url=QDRANT_URL)


class QueryRequest(BaseModel):
    text: str

class RoutingResponse(BaseModel):
    intent: str
    confidence: float
    routing_time_ms: float
    action_taken: str


@app.post("/route", response_model=RoutingResponse)
async def route_query(request: QueryRequest):
    start_time = time.time()
    
    #1.Search Qdrant (Vector Search)
    #FastEmbed happens automatically inside the client here
    search_result = client.query(
        collection_name=COLLECTION_NAME,
        query_text=request.text,
        limit=1
    )

    elapsed_ms = (time.time() - start_time) * 1000

    #2.Logic Layer
    if not search_result:
        #Fallback if vector DB is empty or fails
        return RoutingResponse(
            intent="unknown", 
            confidence=0.0, 
            routing_time_ms=elapsed_ms,
            action_taken="Sent to General Support Queue"
        )

    top_hit = search_result[0]
    score = top_hit.score
    detected_intent = top_hit.metadata['intent']

    #3.Decision Matrix
    if score >= CONFIDENCE_THRESHOLD:
        action = f"Routed to {detected_intent.upper()} Handler"
        final_intent = detected_intent
    else:
        #If the AI isn't sure, don't guess. Send to human/LLM.
        action = "Confidence Low - Routed to GPT-4 for analysis"
        final_intent = "fallback_llm"

    #4.Return JSON
    return RoutingResponse(
        intent=final_intent,
        confidence=round(score, 4),
        routing_time_ms=round(elapsed_ms, 2),
        action_taken=action
    )
