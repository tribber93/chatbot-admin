from .functions import create_retriever, store, delete_a_chunk_doc, client, vector_db
from langchain_community.document_loaders import UnstructuredFileLoader
from unstructured.cleaners.core import clean_extra_whitespace
from celery import shared_task
import time

retriever = create_retriever()

@shared_task
def ingest_data(path, id: int):
    start_time = time.time()
    loader = UnstructuredFileLoader(file_path=path,
                                    post_processors=[clean_extra_whitespace],
                                    strategy="hi_res",
                                    )
    docs = loader.load()
    docs[0].metadata['id'] = id

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
    # delete_a_chunk_doc(file_path)
    return f"Data berhasil dihapus dari database"