import os
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

load_dotenv()

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

fs = LocalFileStore("./docstore")
store = create_kv_docstore(fs)
vector_db = Chroma(
    collection_name="split_parents",
    embedding_function=hf_embeddings,
    persist_directory="./chroma_db"
)

def delete_a_chunk_doc(file_path):
    ids = vector_db._collection.get(where={"source": file_path})['ids']
    if ids == []:
        return
    print("count before", vector_db._collection.count())
    vector_db._collection.delete(ids=ids)
    print("count after", vector_db._collection.count())

def create_retriever(vector_db, store):
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1024)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=256)
    # store = InMemoryStore()

    parent_retriever = ParentDocumentRetriever(
        vectorstore=vector_db,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    
    return parent_retriever
