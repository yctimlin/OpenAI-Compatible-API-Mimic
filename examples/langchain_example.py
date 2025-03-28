"""
Example of using OpenAI-Compatible API Mimic with LangChain.

This script demonstrates how to use the OpenAI-Compatible API Mimic with LangChain,
showing that it can be used as a drop-in replacement for the OpenAI API.

Prerequisites:
- OpenAI-Compatible API Mimic running on http://localhost:8000
- Required packages: langchain, langchain-openai
"""

import os
from typing import List
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Set the OpenAI API base URL to point to our mimic API
os.environ["OPENAI_API_BASE"] = "http://localhost:8000/v1"
os.environ["OPENAI_API_KEY"] = "dummy-key"  # This key is not used but required

def main():
    # Load sample documents
    with open("sample_data.txt", "w") as f:
        f.write("""
        OpenAI-Compatible API Mimic is a powerful tool for AI applications.
        It provides a compatible interface to OpenAI's API for custom backends.
        This allows developers to use existing tools and libraries with their own models.
        The API Mimic supports chat completions, embeddings, and model listing endpoints.
        """)
    
    loader = TextLoader("sample_data.txt")
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    # Create embeddings and store in FAISS index
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # Create a retriever from the vectorstore
    retriever = vectorstore.as_retriever()
    
    # Create a chat model
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Create a conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create a conversational retrieval chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    
    # Example queries
    queries = [
        "What is OpenAI-Compatible API Mimic?",
        "What endpoints does it support?",
        "Why would I use this instead of directly using OpenAI?"
    ]
    
    # Run the chain for each query
    for query in queries:
        print(f"\nQuestion: {query}")
        result = qa_chain.invoke({"question": query})
        print(f"Answer: {result['answer']}")

if __name__ == "__main__":
    main()
    
    # Clean up
    import os
    if os.path.exists("sample_data.txt"):
        os.remove("sample_data.txt") 