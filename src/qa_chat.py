# src/qa_chat.py

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

INDEX_PATH = "faiss_index"

# 1. Load your vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

# 2. Create the QA chain
llm = ChatOpenAI(model="gpt-4o")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True  # Optional: Shows which chunk it answered from
)

# 3. Ask questions
print("💬 Ask a question (type 'exit' to quit):\n")
while True:
    query = input("👉 ")
    if query.lower() == "exit":
        break

    result = qa_chain.invoke({"query": query})
    print("\n🧠 Answer:\n", result["result"])
