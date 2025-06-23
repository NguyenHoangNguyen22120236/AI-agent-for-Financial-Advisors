import os
import tiktoken
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Helper to truncate long text to max token limit
def truncate_to_max_tokens(text: str, max_tokens: int, model="text-embedding-3-small") -> str:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens])

# Generate embedding with safe input length
def generate_embedding(text: str) -> list[float]:
    truncated_text = truncate_to_max_tokens(text, max_tokens=8191, model="text-embedding-3-small")
    response = client.embeddings.create(
        input=[truncated_text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
