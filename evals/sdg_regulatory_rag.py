import sys
import os
import time
from datetime import datetime
from uuid import uuid4
import unstructured

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from loaders.load_pdf_from_s3 import load_pdf_from_public_s3
from ragas.testset import TestsetGenerator
from langsmith import Client
from tqdm import tqdm
from langchain_community.document_loaders import DirectoryLoader
from utils.document_parsers import extract_text_with_metadata
from dotenv import load_dotenv

load_dotenv()


def create_knowledge_graph():
    data_dir = "/Users/pratikmurali/code/aiml-workspaces/fda-regulatory-assistant/evals/data/fda"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading text files from {data_dir}...")
    loader = DirectoryLoader(data_dir, glob="*.txt")
    docs = loader.load()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(docs)} text documents")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating test dataset...")
    
    generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1-mini"))
    generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
    
    generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
    dataset = generator.generate_with_langchain_docs(docs, testset_size=10)
    return dataset


def create_langsmith_dataset():
    client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating LangSmith dataset...")
    langsmith_dataset = client.create_dataset(dataset_name="fda_guidance_samd_"+str(uuid4()), description="FDA Guidance for SAMD dataset")
    dataset = create_knowledge_graph()
    
    df = dataset.to_pandas()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Uploading {len(df)} examples to LangSmith...")
    
    for data_row in tqdm(df.iterrows(), total=len(df), desc="Uploading examples"):
        client.create_example(
            inputs={
                "question": data_row[1]["user_input"]   
            },
            outputs={
                "answer": data_row[1]["reference"]
            },
            metadata={
                "context": data_row[1]["reference_contexts"]
            },
            dataset_id=langsmith_dataset.id
        )
    
    print(f"✅ Successfully created LangSmith dataset with {len(df)} examples")


if __name__ == "__main__":
    start_time = time.time()
    create_langsmith_dataset()
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
