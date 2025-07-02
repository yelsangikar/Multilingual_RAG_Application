from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.documents import Document
from doc_loader import extract_images_from_pdf, extract_text_from_image_with_gpt
from langchain_community.document_loaders import PyMuPDFLoader

import os
from tempfile import NamedTemporaryFile

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename.lower()
    ext = filename.split(".")[-1]
    contents = await file.read()

    # Save to a temporary file
    with NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    docs = []
    try:
        if ext == "pdf":
            loader = PyMuPDFLoader(tmp_path)
            docs.extend(loader.load())

        elif ext in ["png", "jpg", "jpeg"]:
            extracted = extract_text_from_image_with_gpt(tmp_path)
            docs.append(Document(page_content=extracted, metadata={"source": filename}))

        elif ext == "txt":
            text = contents.decode("utf-8")
            docs.append(Document(page_content=text, metadata={"source": filename}))

        else:
            return JSONResponse(content={"error": "Unsupported file type"}, status_code=400)

    finally:
        os.remove(tmp_path)

    return {"message": "Upload successful", "preview": docs[0].page_content[:500]}

INDEX_PATH = "faiss_index"

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat_with_faiss(request: ChatRequest):
    if not os.path.exists(INDEX_PATH):
        raise HTTPException(status_code=400, detail="No FAISS index found. Please upload and process documents first.")

    # Load index and setup QA chain
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(model="gpt-4o")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # Run query
    try:
        answer = qa.run(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")

