import os
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from bs4 import BeautifulSoup
import markdown
import regex as re
from django.db.models import F
from langchain_core.prompts import ChatPromptTemplate

from admin_chatbot.functions import find_matching_context
from admin_chatbot.models import ChatHistory, FileUpload
from rag_task.functions import create_retriever#, base_retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
from rag_task.chromadb import retriever
# from rag_task.qdrantdb import retriever

output_parser = StrOutputParser()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

template = """
kamu adalah asisten virtual yang membantu memberikan informasi akademik dan non-akademik di Universitas Catur Insan Cendekia
jawab pertanyaan hanya berdasarkan pada CONTEXT yang diberikan.
jika jawaban tidak ada pada CONTEXT, respon dengan mengulang hal apa yang ditanyakan tidak ada dalam konteks yang diberikan. 
Jangan meresponse dalam format Markdown

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
        "Maaf", "tidak tersedia",
        # "tidak bisa", 
        "tidak ada informasi", "tidak ditemukan", "belum ada informasi", 
        # "tidak diketahui", "tidak dapat",
        "tidak tersedia dalam dokumen yang diberikan"
    ]
    
    # # Memeriksa apakah salah satu kata kunci ada dalam respon
    for keyword in keywords:
        if keyword.lower() in response.lower():
            return True
    return False
    # result = all(kata in response.lower() for kata in keywords)
    
    # return result

def generate_chat(query, clean_response=False, plain_text=False):
    
    """ Ini merupakan fungsi untuk menghasilkan teks dari pertanyaan pengguna
    
    Args:
    query: merupakan input pertanyaan (str)
    clean_response: digunakan untuk membersihkan teks output (bool)
    plain_text: digunakan untuk menghasilkan output teks biasa (bool)

    Returns:
        Map: berisi question dan answer
    """
    result = chain_with_source().invoke(query)
        
    output = {
        "question": query,
        "answer": result['answer'],
        # "context": result['context'],
    }
    
    print(result['context'])
    if clean_response:
        output["answer"] = re.sub(r'\*\*(.*?)\*\*', r'*\1*', output["answer"])
    
    if result['context'] != []:
        is_answered = not is_unanswerable_response(output["answer"])
        
        if len(result['context']) >= 2:
            context = find_matching_context(query, result['context'][0], result['context'][1])
            doc_id = context.metadata['id']
        else:
            context = result['context'][0]
            doc_id = context.metadata['id']
            
        # print(is_answered)
        if is_answered:
            FileUpload.objects.filter(id=doc_id).update(count_retrieved=F('count_retrieved') + 1)
            
        ChatHistory.objects.create(message=query, file_upload_id=doc_id, is_answered=is_answered)
        
    return output


def markdown_to_text(markdown_string, html_format=False):
    # Convert markdown to HTML
    html_text = markdown.markdown(markdown_string)
    # Use BeautifulSoup to parse the HTML and extract text
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Get the text with list items preserved
    if html_format:
        return f"<html> \n\t{str(soup)}\n</html>"
    else:
        text_with_lists = extract_text_preserving_lists(soup)
        return text_with_lists

# Function to extract text while preserving list items
def extract_text_preserving_lists(soup):
    result = []
    for element in soup.recursiveChildGenerator():
        if element.name == 'li':
            parent = element.find_parent(['ul', 'ol'])
            if parent.name == 'ol':
                result.append(f"{element.find_previous_siblings('li').count() + 1}. {element.get_text()}")
            else:
                result.append(f"- {element.get_text()}")
        elif element.name in ['p', 'div'] and element.get_text(strip=True):
            result.append(element.get_text())
    return '\n'.join(result)