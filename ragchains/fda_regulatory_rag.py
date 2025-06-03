from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain.storage import LocalFileStore
from prompts.rag_prompts import fda_rag_prompt_template
from langchain.schema.output_parser import StrOutputParser
from langchain.embeddings import CacheBackedEmbeddings
from langchain_core.caches import InMemoryCache
from langchain.globals import set_llm_cache
from langchain_redis import RedisSemanticCache
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from loaders.load_pdf_from_s3 import load_pdf_from_public_s3
import tiktoken
import hashlib

load_dotenv()


def tiktoken_len(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)


def format_docs_with_sources(docs):
    """Format documents with source information for the prompt"""
    formatted_docs = []
    for i, doc in enumerate(docs):
        source_info = doc.metadata.get("source", "Unknown source")
        page_info = doc.metadata.get("page", "Unknown page")

        # Extract original source file name from the full source path
        if "s3://" in source_info:
            original_source = source_info.split("/")[-1].replace(".pdf", "")
        else:
            original_source = source_info

        formatted_doc = f"[Source {i + 1}: {original_source}, Page {page_info}]\n{doc.page_content}\n"
        formatted_docs.append(formatted_doc)

    return "\n".join(formatted_docs)


def extract_sources_from_docs(docs):
    """Extract unique source references from retrieved documents"""
    sources = []
    seen_sources = set()

    for doc in docs:
        source_info = doc.metadata.get("source", "Unknown source")
        page_info = doc.metadata.get("page", "Unknown page")

        # Extract original source file name
        if "s3://" in source_info:
            original_source = source_info.split("/")[-1].replace(".pdf", "")
        else:
            original_source = source_info

        source_key = f"{original_source}_page_{page_info}"
        if source_key not in seen_sources:
            sources.append(
                {
                    "document": original_source,
                    "page": page_info,
                    "full_source": source_info,
                }
            )
            seen_sources.add(source_key)

    return sources


def fda_regulatory_rag(docs: list[Document]):
    # create a llm-token aware text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=80, length_function=tiktoken_len
    )
    split_docs = text_splitter.split_documents(docs)

    # set the embedding model
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    # Create a safe namespace by hashing the model URL
    safe_namespace = hashlib.md5(embedding_model.model.encode()).hexdigest()

    # Create a cache-backed embeddings instance
    store = LocalFileStore("./cache/")
    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        embedding_model, store, namespace=safe_namespace
    )

    # Create vectorstore
    vectorstore = Qdrant.from_documents(
        split_docs,
        cached_embedder,
        location=":memory:",
        collection_name="fda_guidance_for_samd_and_aiml",
    )
    # set the llm model
    fda_regulatory_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    # Try to use Redis cache, fall back to InMemoryCache if Redis is unavailable
    # create_redis_semantic_cache(embedding_model)
    set_llm_cache(InMemoryCache())

    # create a retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    )

    # Custom function to retrieve documents and format them
    def retrieve_and_format(question):
        docs = retriever.invoke(question)
        return {
            "context": format_docs_with_sources(docs),
            "question": question,
            "source_documents": docs,
        }

    # LCEL Chain with source tracking
    fda_regulatory_rag_chain = (
        RunnableLambda(retrieve_and_format)
        | RunnablePassthrough.assign(
            answer=fda_rag_prompt_template | fda_regulatory_llm | StrOutputParser()
        )
        | RunnableLambda(
            lambda x: {
                "answer": x["answer"],
                "sources": extract_sources_from_docs(x["source_documents"]),
                "source_documents": x["source_documents"],  # Include raw source documents for evaluation
            }
        )
    )
    return fda_regulatory_rag_chain


def create_redis_semantic_cache(embedding_model):
    try:
        # redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_url = "redis://127.0.0.1:6379"
        print(f"Attempting to connect to Redis at {redis_url}")
        semantic_cache = RedisSemanticCache(
            redis_url=redis_url,
            embeddings=embedding_model,
            distance_threshold=0.05,
            ttl=3600,  # Cache entries expire after 1 hour
            name="fda_regulatory_rag_cache",
            prefix="fda_regulatory_rag_cache",
        )
        set_llm_cache(semantic_cache)
        print("Successfully connected to Redis cache")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        print("Falling back to InMemoryCache")
        set_llm_cache(InMemoryCache())


if __name__ == "__main__":
    print("🔄 Loading FDA regulatory documents from S3...")
    docs = load_pdf_from_public_s3("s3://fda-samd-regulatory-guidance/")
    print(f"✅ Loaded {len(docs)} regulatory documents")
    print("🔄 Building regulatory RAG chain...")
    chain = fda_regulatory_rag(docs)
    response = chain.invoke(
        "What documents are required for a 510K submission for a Class II medical device?"
    )
    print(response)
