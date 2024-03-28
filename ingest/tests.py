import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.vectorstores import Chroma

def clean_text(text):
    # Menghapus karakter khusus seperti \n, \r, dll.
    cleaned_text = re.sub(r'[\n\r\t]+', ' ', text)

    # Menghapus spasi ganda
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Menghapus tag HTML jika ada
    cleaned_text = re.sub(r'<.*?>', '', cleaned_text)

    # Menghapus karakter non-ASCII
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', cleaned_text)

    return cleaned_text

class VectorStore:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.vector_store = Chroma(model_name)

    def get_vector(self, text: str):
        return self.vector_store.get_vector(text)
    
# llm = ChatGoogleGenerativeAI(model="gemini-pro")
# response = llm.invoke("apa arti cinta?")

# hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
#     model_name="firqaaa/indo-sentence-bert-base"
# )

loader = UnstructuredURLLoader(urls=["https://laiybgdrmnbcmmmgxhwj.supabase.co/storage/v1/object/public/pdf/Surat%20Pemberitahuan%20UAS%20Ganjil%202023.2024%20-%20Mahasiswa.pdf?"])
docs = loader.load()
docs = clean_text(docs[0].page_content)
print(docs)