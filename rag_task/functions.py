from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

fs = LocalFileStore("./docstore")
store = create_kv_docstore(fs)

# def delete_a_chunk_doc(file_path):
#     ids = vector_db._collection.get(where={"source": file_path})['ids']
#     if ids == []:
#         return
#     print("count before", vector_db._collection.count())
#     vector_db._collection.delete(ids=ids)
#     print("count after", vector_db._collection.count())

def create_retriever(vector_db):
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=3000)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=512)
    # store = InMemoryStore()
    fs = LocalFileStore("./docstore")
    store = create_kv_docstore(fs)

    parent_retriever = ParentDocumentRetriever(
        vectorstore=vector_db,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        # search_kwargs={"k":2}
    )
    
    return parent_retriever

def get_a_docstore_ids(file_path):
    docstore_ids = list(store.yield_keys())
    ids = []
    for idx, doc in enumerate(store.mget(docstore_ids)):
        if doc.metadata['source'] == file_path:
            ids.append(docstore_ids[idx])
            
    return ids