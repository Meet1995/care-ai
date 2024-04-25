# import os
import json
import openai
import streamlit as st
from care_ai_tools import (
    initiate_firebase_app,
    get_patient_temperature,
    get_patient_spo2,
    get_patient_pulse_or_pulse_rate,
)

# from dotenv import load_dotenv
from care_ai_agent import get_openai_agent


st.title("Care AI")

if ("is_firebase_initialized" not in st.session_state) or (
    not st.session_state.is_firebase_initialized
):
    # load_dotenv(dotenv_path="openai.env")
    openai.api_key = st.secrets["openai_api_key"]
    initiate_firebase_app(st.secrets["db_url"], json.loads(st.secrets["db_json"]))
    st.session_state.is_firebase_initialized = True

if st.button("Reset History"):
    tools = [get_patient_temperature, get_patient_spo2, get_patient_pulse_or_pulse_rate]
    st.session_state.agent = get_openai_agent(tools=tools)
    st.session_state.messages = []

# inittialize agent
if "agent" not in st.session_state:
    tools = [get_patient_temperature, get_patient_spo2, get_patient_pulse_or_pulse_rate]
    st.session_state.agent = get_openai_agent(tools=tools)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = st.session_state.agent.invoke({"input": prompt})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response["output"])
    # # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response["output"]}
    )
