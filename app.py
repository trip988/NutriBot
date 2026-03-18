import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("NutriBot - Your Nutrition Assistant")
st.caption("Ask me about calories, protein, and nutrients in any food or drink!")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are NutriBot, an expert nutrition assistant.
        When asked about any food or drink, always provide:
        - Calories
        - Protein content
        - Carbohydrates
        - Fats
        - Key vitamins and minerals
        - A short health tip
        Be concise, friendly and helpful."""}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Ask about any food or drink..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
