# AI-Based Chatbot System with Retrieval-Augmented Generation (RAG)

## Overview
In today’s digital era, quick and accurate information access is crucial, especially in education. To address this need, I developed an AI-based chatbot system for **Catur Insan Cendekia University** using the **Retrieval-Augmented Generation (RAG)** method. This system provides fast, relevant, and contextual information access for students and the public.

---

## What is Retrieval-Augmented Generation (RAG)?
RAG is an innovative approach that combines two main components:
1. **Indexing and Retrieval**
2. **Generation**

This method enables the system to:
- Search and retrieve relevant information from a database.
- Process and generate contextual, informative responses.

---

## How It Works

### 1. Indexing
- Documents are structured hierarchically into **“parent chunks”** and **“child chunks”**.
- Each chunk is transformed into vectors using embedding models like **Sentence-BERT** to improve semantic accuracy.

### 2. Retrieval
- Utilizes a **Parent Document Retriever** to locate the most relevant data based on user queries.
- Pinpoints the exact **child chunk** while providing the **parent chunk** as context for a comprehensive response.

### 3. Augmented Information
- The retrieved data is enhanced with:
  - Language model instructions.
  - Vector database context.
  - User query inputs.

### 4. Generation
- The enhanced information is processed using a **large language model (LLM)** such as **Gemini AI** to generate coherent and informative responses.

---

## Tools Used
To build this RAG-based chatbot, the following tools and technologies were utilized:

- **[LangChain](https://www.langchain.com/)**: Framework for building applications powered by LLMs.
- **[HuggingFace](https://huggingface.co/)**: Pre-trained NLP models for embedding and text processing.
- **[ChromaDB](https://www.trychroma.com/)**: Vector database for storing embeddings.
- **[Gemini AI](https://deepmind.google/technologies/gemini/)**: Large language model for generating responses.
- **[Unstructured IO](https://unstructured.io/)**: Document processing and structuring.
- **[Django](https://www.djangoproject.com/)**: Backend framework for building the API.
- **Redis**: Fast data storage for caching.
- **Celery**: Task queue for asynchronous processing.
- **Other Tools**: Various Python libraries to support the implementation.

---

## Features
- **Fast and Relevant Responses**: Provides accurate and contextual answers to user queries.
- **Information Hierarchy**: Structures documents to ensure efficient retrieval.
- **Educational Focus**: Tailored to meet the needs of students and the academic community.

---

## Screenshots

### Chat Interface
<div style="display: flex; justify-content: space-between; flex-wrap: wrap;">

<div style="width: 48%; margin-bottom: 10px;">
<img src="https://media.licdn.com/dms/image/v2/D562DAQHeJXfiQjtcdA/profile-treasury-image-shrink_1920_1920/profile-treasury-image-shrink_1920_1920/0/1730108056490?e=1736470800&v=beta&t=PawkFXsElFBuZadV9fSCT5-q5mTjoPKZGI3U2VggQ4s" alt="Chat Interface 1" style="width: 100%; border: 1px solid #ccc;">
<p style="text-align: center; font-size: 14px; margin-top: 5px;">Chat Interface 1</p>
</div>

<div style="width: 48%; margin-bottom: 10px;">
<img src="https://media.licdn.com/dms/image/v2/D562DAQHqn-ZlxQgABQ/profile-treasury-image-shrink_1920_1920/profile-treasury-image-shrink_1920_1920/0/1730108067829?e=1736470800&v=beta&t=4BSB1O4ow8vuoYLxrlR4eWoEJhiojwfBKDBBXXUksnI" alt="Chat Interface 2" style="width: 100%; border: 1px solid #ccc;">
<p style="text-align: center; font-size: 14px; margin-top: 5px;">Chat Interface 2</p>
</div>

</div>

---

## Impact
By applying the **RAG method**, this chatbot significantly improves the accessibility and efficiency of information services in educational settings. It offers a scalable solution for modern institutions aiming to enhance their digital services.

---

## Repository
This project demonstrates the practical application of **AI-based chatbots** and **RAG techniques** in real-world scenarios. For further details, please visit the GitHub repository:

**[Chatbot Admin System](https://github.com/tribber93/chatbot-admin)**

---

## Skills Demonstrated
- **Large Language Models (LLM)**
- **Retrieval-Augmented Generation (RAG)**
- **Natural Language Processing (NLP)**
- **LangChain Framework**
- **Information Retrieval**
- **Backend Development with Django**
