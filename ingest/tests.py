import os
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from dotenv import load_dotenv
from django.conf import settings
from my_class import MyVectorDatabase, create_retriever
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

load_dotenv()
# settings.configure()
fs = LocalFileStore("./docstore")
store = create_kv_docstore(fs)

# print(os.path.join(settings.MEDIA_URL,'documents/Pengumuman_Her_registrasi_dan_KRS_Semester_Ganjil_Tahun_Akademik_2023-2024_-_W_33SBFkh.pdf'))
# path = "media\documents\Pengumuman_Her_registrasi_dan_KRS_Semester_Ganjil_Tahun_Akademik_2023-2024_-_W_33SBFkh.pdf"
path = "media\documents\Jadwal_Perkuliahan_Semester_Genap_TA_2023-2024_9_Maret_24.pdf"

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = 'test'

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('HF_TOKEN'), model_name="firqaaa/indo-sentence-bert-base" #"intfloat/multilingual-e5-base"
)

client = MyVectorDatabase(qdrant_url, qdrant_api_key, collection_name)
vector_db = client.vector_store(hf_embeddings)
# print(client.count_all_chunk())

#Load document
loader = UnstructuredPDFLoader(path)
docs = loader.load()

retriever = create_retriever(vector_db, store)

retriever.add_documents(docs)

# ingest_data.delay(path)