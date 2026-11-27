"""
#--------------------------------------------------------------------
# Script that reads PDF, spilts the PDF into chucks SentenceSplitter,
# and embeds the chunks (prepares the data).
#--------------------------------------------------------------------
"""

from anthropic import Anthropic
from openai import OpenAI
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

splitter =SentenceSplitter(chunk_size=1000, chunk_overlap=200) # Chuncker, chunk size, and chunk overlap

def load_and_chunk_pdf(path: str):
    """Function that loads pdf and chunks the text into managable sizes"""
    docs = PDFReader().load_data(file=path) # Path for script to load PDF
    texts = [d.text for d in docs if getattr(d, "text", None)] # Get the text content for every doc if doc has text attribute
    
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))

    return chunks

def embed_text(texts: list[str]) -> list[list[float]]:
    """Function that sends request to OpenAI, embeds text, and pulls the embeddings"""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )

    return [item.embeddings for item in response.data]