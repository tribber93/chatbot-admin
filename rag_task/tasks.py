from langchain_community.document_loaders import UnstructuredFileLoader
from unstructured.cleaners.core import clean_extra_whitespace
# from rag_task.qdrantdb import retriever
from rag_task.chromadb import retriever
from celery import shared_task
import time

@shared_task
def ingest_data(path, id: int):
    start_time = time.time()
    loader = UnstructuredFileLoader(file_path=path,
                                    post_processors=[clean_extra_whitespace],
                                    # strategy="hi_res",
                                    )
    docs = loader.load()
    docs[0].metadata['id'] = id

    retriever.add_documents(docs)
    end_time = time.time()

    # Hitung lama waktu yang dibutuhkan
    duration = end_time - start_time
    return f"Lama waktu yang dibutuhkan: {duration} detik"