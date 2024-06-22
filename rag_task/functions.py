import os
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
# from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

from rag_task.qdrantdb import MyVectorDatabase

load_dotenv()

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

fs = LocalFileStore("./docstore")
store = create_kv_docstore(fs)
# vector_db = Chroma(
#     collection_name="split_parents",
#     embedding_function=hf_embeddings,
#     persist_directory="./chroma_db"
# )

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv('COLLECTION_NAME')

client = MyVectorDatabase(qdrant_url, qdrant_api_key, collection_name)
vector_db = client.vector_store(hf_embeddings)

def delete_a_chunk_doc(file_path):
    ids = vector_db._collection.get(where={"source": file_path})['ids']
    if ids == []:
        return
    print("count before", vector_db._collection.count())
    vector_db._collection.delete(ids=ids)
    print("count after", vector_db._collection.count())

def create_retriever():
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=3000)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=512)
    # store = InMemoryStore()
    fs = LocalFileStore("./docstore")
    store = create_kv_docstore(fs)

    parent_retriever = ParentDocumentRetriever(
        vectorstore=vector_db,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        search_kwargs={"k":2}
    )
    
    return parent_retriever

