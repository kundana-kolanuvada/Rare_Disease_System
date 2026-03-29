import os
import logging

# 1. Force-Disable Tracing and hide the API key
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = "disabled" # Prevents 'None' errors

# 2. Silence the specific LangChain/HTTP loggers causing the spam
logging.getLogger('langsmith').setLevel(logging.CRITICAL)
logging.getLogger('langchain.callbacks.tracers.langchain').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

def get_llm():
    """
    Returns initialized LLM (Groq)
    """
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0
    )
