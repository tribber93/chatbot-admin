
import os
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from rag_task.functions import get_a_docstore_ids, store
from rag_task.functions import create_retriever

class MyVectorDatabase():
    def __init__(self, qdrant_url, qdrant_api_key, collection_name):
        self.collection_name = collection_name

        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            prefer_grpc=True,
            api_key=qdrant_api_key,
        )
        if not self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.create_collection(
                collection_name,
                vectors_config=models.VectorParams(
                size=768,
                distance=models.Distance.COSINE
            ))

    def vector_store(self, embeddings):
        vector_db = Qdrant(
            client=self.qdrant_client,
            embeddings=embeddings,
            collection_name=self.collection_name,
        )

        return vector_db

    def count_all_chunk(self):
        return self.qdrant_client.count(self.collection_name).count

    def get_ids_a_document_chunk(self, file_path):
        records, _ = self.qdrant_client.scroll(
            collection_name=self.collection_name,
            limit=self.count_all_chunk(),
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key='metadata.source',
                                          match=models.MatchValue(value=file_path)),
                ]
            ),
        )

        ids = [record.id for record in records]

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

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("COLLECTION_NAME")

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

client = MyVectorDatabase(qdrant_url, qdrant_api_key, collection_name)
vector_db = client.vector_store(hf_embeddings)


retriever = create_retriever(vector_db)