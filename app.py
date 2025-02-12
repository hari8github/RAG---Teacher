from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter

model_local = ChatOllama(model = "mistral")

# 1. Splitting data into chunks

urls = [
    "https://www.liverpoolfc.com/"
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size = 7500, chunk_overlap=100)
doc_splits = text_splitter.split_documents(docs_list)

# 2. Convert docs to embeddings and store them

vectorstores = Chroma.from_documents(
    documents = doc_splits,
    collection_name="rag-chroma",
    embedding = OllamaEmbeddings()
)

retriever = vectorstores.as_retriever()

# 3. Before RAG
print("Before RAG\n")

before_rag_templates = "What is {topic}"
before_rag_prompt = ChatPromptTemplate.from_template(before_rag_templates)
before_rag_chain = before_rag_prompt | model_local | StrOutputParser()
print(before_rag_chain.invoke({"topic": "Wi-Fi"}))

# 4. After RAG
print("\n After RAG\n")
after_rag_templates = """Answer the question based only on the following context: 
{context} 
Question: {question}"""
after_rag_prompt = ChatPromptTemplate.from_template(after_rag_templates)
after_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | after_rag_prompt | model_local | StrOutputParser()
)

print(after_rag_chain.invoke("Give a summary about this page"))