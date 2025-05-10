from langchain.chat_models import init_chat_model
import streamlit as st
import openai
from dotenv import load_dotenv
import os

from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import streamlit as st

st_callback = StreamlitCallbackHandler(st.container())

# Load the environment variables from .env file
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

llm = init_chat_model("gpt-4.1-nano-2025-04-14", model_provider="openai", temperature=0)

st.title("Investor assistant")