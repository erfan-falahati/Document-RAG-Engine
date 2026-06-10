import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .vector_store import search_similar_documents

def get_openrouter_llm():
    """Initializes connection to OpenRouter passing through direct host bridge."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Updated to 172.17.0.1 and port 10808 based on system configuration
    custom_http_client = httpx.Client(
        proxy="http://172.17.0.1:10808",
        timeout=30.0
    )

    return ChatOpenAI(
        model_name="deepseek/deepseek-v4-flash:free",
        extra_body={
            "models": [
                "deepseek/deepseek-v4-flash:free",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "openai/gpt-oss-120b:free",
            ],
            "route": "fallback"
        },

        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        http_client=custom_http_client, 
        default_headers={
            "HTTP-Referer": "http://localhost:8000", 
            "X-Title": "DjangoDocQA"
        }
    )

def generate_answer(question):
    """Full RAG pipeline: retrieves docs and generates answer."""
    related_docs = search_similar_documents(question)
    
    if not related_docs:
        return "No related documents found!" 

    context_text = "\n\n".join([doc.page_content for doc in related_docs])

    prompt_template = """
    You are a helpful assistant. Answer the user's question ONLY using the provided context. 
    If you don't know the answer based on the context, say so. Answer in the language the question was asked.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    prompt = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )
    
    llm = get_openrouter_llm()
    chain = prompt | llm
    
    response = chain.invoke({"context": context_text, "question": question})
    
    return response.content
