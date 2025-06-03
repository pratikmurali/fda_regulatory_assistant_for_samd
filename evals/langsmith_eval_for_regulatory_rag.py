import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith.evaluation import LangChainStringEvaluator, evaluate
from langchain_openai import ChatOpenAI
from ragchains.fda_regulatory_rag import fda_regulatory_rag
from loaders.load_pdf_from_s3 import load_pdf_from_public_s3


def evaluate_regulatory_rag(dataset:str):
    eval_llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    qa_evaluator = LangChainStringEvaluator("qa", config={"llm" : eval_llm})
    contextual_qa_evaluator = LangChainStringEvaluator("context_qa", config={"llm" : eval_llm})
    chain_of_thought_evaluator = LangChainStringEvaluator("cot_qa", config={"llm" : eval_llm})
    labeled_helpfulness_evaluator = LangChainStringEvaluator(
    "labeled_criteria",
    config={
        "criteria": {
            "helpfulness": (
                "Is this submission helpful to the user,"
                " taking into account the correct reference answer?"
            )
        },
        "llm" : eval_llm
    },
    prepare_data=lambda run, example: {
        "prediction": run.outputs["output"],
        "reference": example.outputs["answer"],
        "input": example.inputs["question"],
    }
)
    
    # Load documents and initialize the chain
    print("🔄 Loading FDA regulatory documents from S3...")
    docs = load_pdf_from_public_s3("s3://fda-samd-regulatory-guidance/")
    print(f"✅ Loaded {len(docs)} regulatory documents")
    print("🔄 Building regulatory RAG chain...")
    chain = fda_regulatory_rag(docs)
    
    # Create a wrapper function to handle dictionary inputs
    def chain_wrapper(input_data):
        # If input is a dictionary with a 'question' key, extract the question
        if isinstance(input_data, dict) and "question" in input_data:
            query = input_data["question"]
        else:
            query = str(input_data)  # Convert to string as fallback
        
        # Call the chain with the extracted query
        result = chain.invoke(query)
        
        # Return the result in the format expected by the evaluator
        return {"output": result["answer"]}
    
    return evaluate(
        chain_wrapper,
        data=dataset,
        evaluators=[
            qa_evaluator,
            labeled_helpfulness_evaluator,
            contextual_qa_evaluator,
            chain_of_thought_evaluator
        ],
        metadata={"revision_id": "default_chain_init"},
    )

if __name__ == "__main__":
    print(evaluate_regulatory_rag("fda_guidance_samd_166b1a46-1468-4bed-8fd2-b844a5ccffba"))
