from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.documents import Document
from doc_loader import extract_images_from_pdf, extract_text_from_image_with_gpt
from langchain_community.document_loaders import PyMuPDFLoader

from chunk_and_embed import chunk_documents, load_or_create_index, embed_and_add_new_docs  # 🧠 ← Your helper file

import os
from tempfile import NamedTemporaryFile

from langchain.chains import RetrievalQA

INDEX_PATH = "faiss_index"

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

    with NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    docs = []
    try:
        if ext == "pdf":
            loader = PyMuPDFLoader(tmp_path)
            docs.extend(loader.load())
            for img_path, img_name in extract_images_from_pdf(tmp_path):
                extracted = extract_text_from_image_with_gpt(img_path)
                docs.append(Document(page_content=extracted, metadata={"source": img_name}))
                os.remove(img_path)

        elif ext in ["png", "jpg", "jpeg"]:
            extracted = extract_text_from_image_with_gpt(tmp_path)
            docs.append(Document(page_content=extracted, metadata={"source": filename}))

        elif ext == "txt":
            text = contents.decode("utf-8")
            docs.append(Document(page_content=text, metadata={"source": filename}))

        else:
            return JSONResponse(content={"error": "Unsupported file type"}, status_code=400)

        if not docs:
            return JSONResponse(content={"error": "No content extracted"}, status_code=400)

        # ✅ Chunk + Embed + Index
        chunks = chunk_documents(docs)
        vectorstore, embeddings = load_or_create_index(chunks)
        embed_and_add_new_docs(vectorstore, chunks, embeddings)

    finally:
        os.remove(tmp_path)

    return {"message": "Upload successful", "preview": docs[0].page_content[:500]}

from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat_with_faiss(request: ChatRequest):
    if not os.path.exists(INDEX_PATH):
        raise HTTPException(status_code=400, detail="❌ FAISS index not found. Upload a document first.")

    # Load vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

    # Create retriever and QA chain
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(model="gpt-4o")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    try:
        answer = qa.run(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"💥 Error: {e}")

