from langchain_huggingface import HuggingFaceEmbeddings

model_name = 'firqaaa/indo-sentence-bert-base'
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

hf_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
    cache_folder='./models',
)