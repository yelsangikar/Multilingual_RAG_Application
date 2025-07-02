# src/app.py

import streamlit as st
import requests

st.set_page_config(page_title="📄 Multi-Language RAG", layout="centered")

st.title("📤 Upload Document (PDF, TXT, Image)")

# Upload section
file = st.file_uploader("Upload file", type=["pdf", "png", "jpg", "jpeg", "txt"])
if file is not None:
    bytes_data = file.read()
    filename = file.name
    files = {"file": (filename, bytes_data)}
    upload_response = requests.post("http://127.0.0.1:9000/upload", files=files)

    if upload_response.status_code == 200:
        st.success("✅ Upload successful")
        st.write("📄 Document preview:")
        st.write(upload_response.json()["preview"])
    else:
        st.error("❌ Upload failed")
        st.stop()

# Chat section
st.markdown("---")
st.subheader("💬 Ask a Question about the Uploaded Document")

question = st.text_input("Enter your question:")
if st.button("Ask"):
    if not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        chat_response = requests.post(
            "http://127.0.0.1:9000/chat",
            json={"question": question}
        )

        if chat_response.status_code == 200:
            st.success("🧠 Answer:")
            st.write(chat_response.json()["answer"])
        else:
            st.error(f"❌ Failed to get answer: {chat_response.text}")
