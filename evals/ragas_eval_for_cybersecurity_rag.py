import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from loaders.load_pdf_from_s3 import load_pdf_from_public_s3
from ragas.testset import TestsetGenerator
from langchain_community.document_loaders import DirectoryLoader
from dotenv import load_dotenv
from ragas import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, ResponseRelevancy, ContextEntityRecall, NoiseSensitivity
from ragas import evaluate, RunConfig
from ragchains.fda_cybersecurity_rag import fda_cybersecurity_rag


load_dotenv()


def create_knowledge_graph():
    data_dir = "/Users/pratikmurali/code/aiml-workspaces/fda-regulatory-assistant/evals/data/cybersecurity"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading text files from {data_dir}...")
    loader = DirectoryLoader(data_dir, glob="*.txt")
    docs = loader.load()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(docs)} text documents")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating test dataset...")

    generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1-mini", temperature=0))
    generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

    generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
    dataset = generator.generate_with_langchain_docs(docs, testset_size=10)
    return dataset


def create_ragas_dataset_and_evaluate():
    dataset = create_knowledge_graph()

    # Load documents and initialize the chain
    print("🔄 Loading FDA Cybersecurity documents from S3...")
    docs = load_pdf_from_public_s3("s3://fda-samd-cybersecurity-guidance/")
    print(f"✅ Loaded {len(docs)} cybersecurity documents")
    print("🔄 Building cybersecurity RAG chain...")
    chain = fda_cybersecurity_rag(docs)

    for i, test_row in enumerate(dataset):
        print(f"Processing test row {i+1}/{len(dataset)}: {test_row.eval_sample.user_input[:80]}...")

        # Get response from the chain
        chain_response = chain.invoke(test_row.eval_sample.user_input)

        # Set the response text
        test_row.eval_sample.response = chain_response["answer"]

        # Extract retrieved contexts from source documents
        if "source_documents" in chain_response:
            # Convert source documents to text contexts for RAGAS
            retrieved_contexts = [doc.page_content for doc in chain_response["source_documents"]]
            test_row.eval_sample.retrieved_contexts = retrieved_contexts
        else:
            test_row.eval_sample.retrieved_contexts = []

    print(f"✅ Processed all {len(dataset)} test rows")

    dataset.upload() #uploads to ragas.

    # Create DataFrame AFTER processing all test rows and setting retrieved_contexts
    df = dataset.to_pandas()

    evaluation_dataset = EvaluationDataset.from_pandas(df)
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1-mini", temperature=0))
    custom_run_config = RunConfig(timeout=360)
    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness(), ResponseRelevancy(), ContextEntityRecall(), NoiseSensitivity()],
        llm=evaluator_llm,
        run_config=custom_run_config
    )

    return result


if __name__ == "__main__":
    start_time = time.time()
    result = create_ragas_dataset_and_evaluate()
    print(f"Evaluation results: {result}")
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
