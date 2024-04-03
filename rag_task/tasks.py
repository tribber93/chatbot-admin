from .functions import create_retriever, vector_db, store, delete_a_chunk_doc
from langchain_community.document_loaders import UnstructuredPDFLoader
from celery import shared_task
import time

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
    
    delete_a_chunk_doc(file_path)
    return f"Data berhasil dihapus dari database"