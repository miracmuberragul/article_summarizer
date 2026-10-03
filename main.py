"""
Amaç:
    Kullanıcı yüklediği makalenin özetini isteyebilecekyada makaledeki bilgiler hakkında soru sorup cevabını alabilcek. 
    Bunu bir RAG (Retrieval-Augmented Generation) sistemi ile gerçekleştirecek. Vektör veritabanı olarak Faiss kullanılacak.

Kullanılacak teknolojiler:
    - langchain
    - vektör veritabanı : FAISS
    - Dil modeli : gemma:4b
    - Ollama 
    - Uı : Streamlit
    - PDF dosyalarını yüklemek için : PyPDFLoader

KURULUMLAR: 
pip install streamlit langchain_ollama langchain_classic langchain_community faiss-cpu sentence-transformers langchain pyPDF2


"""

from langchain_ollama import ChatOllama
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS # langchain_classic yerine langchain_community
from langchain_community.embeddings import HuggingFaceEmbeddings  # langchain_class
from langchain_community.document_loaders import PyPDFLoader # langchain_classic yerine langchain_community
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter # langchain_classic yerine

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import tempfile

app = FastAPI()
qa_chain = None

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global qa_chain

    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name  # Geçici dosyanın yolu

    # PDF yükle
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    # Metinleri parçala yani chunklara böl
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    # LaBSE embedding ile metin vektörleştirme (Bge yerine normal HuggingFaceEmbeddings ile düzeltildi)
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/LaBSE")

    # FAISS ile vektör veri tabanı
    vectordb = FAISS.from_documents(docs, embedding)

    # Memory ve gemma:4b'yi tanımla
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOllama(model="gemma3:4b", temperature=0.2)

    # RAG + memory zinciri oluştur
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
        memory=memory
    )

    return JSONResponse(content={"message": "PDF başarıyla işlendi."})
    
class QuestionRequest(BaseModel):
    question: str

@app.post("/chat/")
async def chat(request: QuestionRequest):

    if qa_chain is None:
        return {
            "error": "Önce bir PDF yüklemelisiniz."
        }

    response = qa_chain.invoke({
        "question": request.question
    })

    return {
        "answer": response["answer"]
    }
