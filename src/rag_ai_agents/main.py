import datetime
import inngest
import inngest.fast_api # Adapter that connects inngest to a FastAPI app
import logging
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI
from inngest.experimental import ai

load_dotenv() # Load environment variables

# Create the inngest client that serves as the hub for the app
inngest_client = inngest.Inngest(
    app_id="rag_app", # Name of the app in inngest dashboard
    logger=logging.getLogger("uvicorn"), # Inngest logs to uvicorn's console output
    is_production=False, # While in development mode, set to false
    serializer=inngest.PydanticSerializer() # Converts Pydantic models to/from json for step results
)

# Decorator to wrap the PDF inngest 
@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf") # Trigger to ingest client server
)

# Async functions are needed for inngest to allow server to stay responsive while waiting for I/O
# this event is needed for an await on something that is asynchronous 
async def rag_ingest_pdf(context: inngest.Context): 
    return {"hello": "world"}

# Create Fast API web app
app = FastAPI()

# Mount to inngest's HTTP endpoint on the app ("default path /api/inngest")
inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf])