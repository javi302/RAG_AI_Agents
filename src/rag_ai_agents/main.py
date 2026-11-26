import datetime
import inngest
import inngest.fast_api
import logging
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI
from inngest.experimental import ai

load_dotenv() # Load environment variables

# Create clients
inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False, # While in development mode, set to false
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf") # Trigger to ingest client server
)

async def rag_ingest_pdf(context: inngest.Context):
    return {"hello": "world"}

app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf])