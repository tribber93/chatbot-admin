import os
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from dotenv import load_dotenv
from .my_class import MyVectorDatabase, create_retriever
from langchain_community.document_loaders import UnstructuredPDFLoader
from celery import shared_task
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
import time

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = 'test'

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

client = MyVectorDatabase(qdrant_url, qdrant_api_key, collection_name)
vector_db = client.vector_store(hf_embeddings)


fs = LocalFileStore("./docstore")
store = create_kv_docstore(fs)

@shared_task
def ingest_data(path):
    start_time = time.time()
    loader = UnstructuredPDFLoader(path)
    docs = loader.load()

    retriever = create_retriever(vector_db, store)

    retriever.add_documents(docs)
    end_time = time.time()

    # Hitung lama waktu yang dibutuhkan
    duration = end_time - start_time
    return f"Lama waktu yang dibutuhkan: {duration} detik"

def get_a_docstore_ids(file_path):
    docstore_ids = list(store.yield_keys())
    ids = []
    for idx, doc in enumerate(store.mget(docstore_ids)):
        if doc.metadata['source'] == file_path:
            ids.append(docstore_ids[idx])
            
    return ids

def delete_from_vector_db_and_docstore(file_path):
    store_ids = get_a_docstore_ids(file_path)
    store.mdelete(store_ids)
    
    if client.count_all_chunk() != 0:
        vector_ids = client.get_ids_a_document_chunk(file_path)
        if len(vector_ids) != 0:
            vector_db.delete(vector_ids)
    return f"Data berhasil dihapus dari database"