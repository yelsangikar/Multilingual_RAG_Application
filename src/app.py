# src/app.py

import streamlit as st
import requests

st.set_page_config(page_title="📄 Multi-Language RAG", layout="centered")

st.title("📤 Upload Document (PDF, TXT, Image)")

file = st.file_uploader("Upload file", type=["pdf", "png", "jpg", "jpeg", "txt"])
if file is not None:
    bytes_data = file.read()
    filename = file.name
    files = {"file": (filename, bytes_data)}
    response = requests.post("http://127.0.0.1:9000/upload", files=files)

    if response.status_code == 200:
        st.success("✅ Upload successful")
        st.write(response.json()["preview"])
    else:
        st.error("❌ Upload failed")
