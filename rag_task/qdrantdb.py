
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http import models

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