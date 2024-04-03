import os
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from .my_class import MyVectorDatabase, create_retriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
import time

start_time = time.time()

load_dotenv()
# settings.configure()
fs = LocalFileStore("./docstore")
store = create_kv_docstore(fs)
output_parser = StrOutputParser()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = 'test'

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

client = MyVectorDatabase(qdrant_url, qdrant_api_key, collection_name)
vector_db = client.vector_store(hf_embeddings)


llm = ChatGoogleGenerativeAI(model="gemini-pro")
retriever = create_retriever(vector_db, store)

def augmetation():
    template = """
    kamu adalah asisten virtual untuk membantu memberikan informasi akademik di Universitas Catur Insan Cendekia
    jawab pertanyaan berdasarkan konteks yang diberikan dengan response seperti percakapan
    usahakan SELALU menjawab dengan detail dari setiap pertanyaannya.

    CONTEXT: {context}

    </s>
    <|user|>
    {question}
    </s>
    <|assistant|>
    """


    prompt = ChatPromptTemplate.from_template(template)
    
    return prompt

def chain():
    prompt = augmetation()
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )
    
    return chain
