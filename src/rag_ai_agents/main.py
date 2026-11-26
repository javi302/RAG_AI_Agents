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

# Load clients
inngest_client = inngest.Inngest(
    app_id="rag_app",
    logging=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

app = FastAPI()