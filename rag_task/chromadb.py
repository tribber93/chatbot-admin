import os
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from rag_task.functions import create_retriever, get_a_docstore_ids, store

host = os.getenv("CHROMA_HOST")
port = os.getenv("CHROMA_PORT")
hf_token = os.getenv('HF_TOKEN')
collection_name = os.getenv('COLLECTION_NAME')
hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

chroma_client = chromadb.HttpClient(host=host, port=port)

vector_db = Chroma(
    collection_name=collection_name,
    embedding_function=hf_embeddings,
    persist_directory="./chroma_db",
    client=chroma_client
)

retriever = create_retriever(vector_db) #digunakan pada file rag_task.inference_function, rag_task.tasks dan admin_chatbot.views

# Delete Docs
def delete_a_chunk_doc(file_path):
    store_ids = get_a_docstore_ids(file_path)
    store.mdelete(store_ids)
    
    ids = vector_db._collection.get(where={"source": file_path})['ids']
    if ids == []:
        return
    print("count before", vector_db._collection.count())
    vector_db._collection.delete(ids=ids)
    print("count after", vector_db._collection.count())