from django.dispatch import receiver
from admin_chatbot.signals import data_updated
from langchain_core.prompts import ChatPromptTemplate
from .functions import create_retriever#, base_retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

output_parser = StrOutputParser()
llm = ChatGoogleGenerativeAI(model="gemini-pro")
retriever = create_retriever()
template = """
kamu adalah asisten virtual untuk membantu memberikan informasi akademik di Universitas Catur Insan Cendekia
jawab pertanyaan berdasarkan konteks yang diberikan dengan response seperti percakapan
usahakan SELALU menjawab dengan detail dari setiap pertanyaannya.

CONTEXT: {context}

</s>
<|user|>
{question}
</s>
<|assistant|>
"""

@receiver(data_updated)
def handle_data_updated(sender, **kwargs):
    # Tambahkan logika untuk memuat ulang data yang diperlukan
    global store
    fs = LocalFileStore("./docstore")
    store = create_kv_docstore(fs)
    # Misalnya, muat ulang data dari basis data atau cache
    print("Data telah diperbarui. Memuat ulang data...")

prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def chain():
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )
    
    return chain

def chain_with_source():
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    
    return rag_chain_with_source
