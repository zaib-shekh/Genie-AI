import re
import streamlit as st  
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate,
)

st.markdown("""
<style>
    /* Existing Style */
    .main {
            background-color: #1a1a1a;
            color: #ffffff;
            }
    .sidebar .sidebar-content {
            background-color: #2d2d2d;
            }
    .setTextInput textarea {
            color: #ffffff;
            }
    .stSelectbox div[data-baseweb="select"] {
            color: white !important;
            background-color: #3d3d3d !important;
            }
    .stSelectbox  {
            fill: white !important;
            }
    .stSelectbox option {
            background-color: #2d2d2d !important;
            color: white !important;
            }
    div[role="listbox"] div {
            background-color: #2d2d2d !important;
            color: white !important;
            }
</style>                                                   
""", unsafe_allow_html=True)
st.title("🧠 Genie Code Companion")
st.caption("🚀 Your AI Pair Programmer with Debugging Superpowers")

with st.sidebar:
    st.header("⚙️ Configuration")
    select_model = st.selectbox(
        "Select Model",
        ["deepseek-r1:1.5b", "deepseek-r1:3b"],
        index=0
    )
    st.divider()
    st.markdown("### Model Capabilities")
    st.markdown("""
        - 🐍 Python Expert
        - 🐞 Debugging Assistant
        - 📝 Code Documentation
        - 💡 Solution Design
    """)
    st.divider()
    st.markdown("Built with [Ollama](https://ollama.ai/) | [LangChain](https://python.langchain.com/)")
    


# initiate the chat engine
llm_engine = ChatOllama(
    model = select_model,
    base_url = "http://localhost:11434",
    temperature = 0.3,

)
# System prompt configuration
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI coding Assistant. Provide concise, correct solutions "
    "with strategic print statements for debugging. Always respond in English."
)

# Session State management
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm Genie, How can I help you code? 💻"}]

chat_container = st.container()

with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Chat input and processing
user_query = st.chat_input("Type your question here...")        

def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | llm_engine | StrOutputParser()
    raw_response =  processing_pipeline.invoke({})
    clean_response = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL)
    return clean_response

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"])) 
    return ChatPromptTemplate.from_messages(prompt_sequence)

if user_query:
    st.session_state.message_log.append({"role":"user", "content": user_query})

    with st.spinner("🧠 Thinking..."):
        prompt_chain = build_prompt_chain()
        ai_response = generate_ai_response(prompt_chain)

    st.session_state.message_log.append({"role":"ai", "content": ai_response})               
        
    st.rerun()