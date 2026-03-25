from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def get_llm():
    """
    Returns initialized LLM (Groq)
    """
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0
    )