from django.dispatch import receiver
import regex as re
from django.db.models import F
from langchain_core.prompts import ChatPromptTemplate

from admin_chatbot.functions import find_matching_context
from admin_chatbot.models import ChatHistory, FileUpload
from .functions import create_retriever#, base_retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

output_parser = StrOutputParser()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
# llm = ChatGoogleGenerativeAI(model="gemini-pro")
retriever = create_retriever()
template = """
kamu adalah asisten virtual yang membantu memberikan informasi akademik dan non-akademik di Universitas Catur Insan Cendekia
jawab pertanyaan hanya berdasarkan pada CONTEXT yang diberikan.
jika jawaban tidak ada pada CONTEXT, jawab bahwa jawaban tidak ada dalam CONTEXT yang diberikan. 

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
        # RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        RunnablePassthrough.assign()
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    
    return rag_chain_with_source

def is_unanswerable_response(response):
    # # Daftar kata kunci yang menunjukkan ketidakmampuan menjawab
    keywords = [
        "Maaf", "tidak tersedia", "tidak bisa", "tidak ada informasi", 
        "tidak ditemukan", "belum ada informasi", 
        "tidak diketahui", "tidak dapat", "tidak ada",
        "tidak tersedia dalam dokumen yang diberikan"
    ]
    
    # # Memeriksa apakah salah satu kata kunci ada dalam respon
    for keyword in keywords:
        if keyword.lower() in response.lower():
            return True
    return False
    # result = all(kata in response.lower() for kata in keywords)
    
    # return result

def generate_chat(query, clean_response=False):
    result = chain_with_source().invoke(query)
        
    output = {
        "question": query,
        "answer": result['answer'],
    }
    
    if clean_response:
        output["answer"] = re.sub(r'\*\*(.*?)\*\*', r'*\1*', output["answer"])
    
    if result['context'] != []:
        is_answered = not is_unanswerable_response(output["answer"])
        
        if len(result['context']) == 2:
            context = find_matching_context(query, result['context'][0], result['context'][1])
            doc_id = context.metadata['id']
        else:
            context = result['context'][0]
            doc_id = context.metadata['id']
            
        # if is_answered:
        print(is_answered)
        FileUpload.objects.filter(id=doc_id).update(count_retrieved=F('count_retrieved') + 1)
            
        ChatHistory.objects.create(message=query, file_upload_id=doc_id, is_answered=is_answered)
        
    return output