from django.dispatch import receiver
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
jawab pertanyaan berdasarkan konteks yang diberikan dengan response seperti percakapan.
Jika pertanyaan tidak dapat dijawab atau tidak ada dalam CONTEXT, maka cukup menjawab "Maaf saya tidak tahu, silakan hubungi info@cic.ac.id untuk informasi lebih lanjut".

CONTEXT: {context}

</s>
<|user|>
{question}
</s>
<|assistant|>
"""

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
