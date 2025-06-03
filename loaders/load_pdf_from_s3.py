import boto3
import tempfile
import os
from botocore import UNSIGNED
from botocore.config import Config
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from urllib.parse import urlparse


def load_pdf_from_public_s3(s3_url: str) -> list[Document]:
    """
    Load PDFs from a public S3 bucket without credentials
    """
    # Parse S3 URL
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    prefix = parsed_url.path.lstrip("/")

    # Create anonymous S3 client
    s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))

    documents = []

    try:
        # List objects in the bucket with the given prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if "Contents" not in response:
            print(f"No objects found in {s3_url}")
            return documents

        # Process each PDF file
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.lower().endswith(".pdf"):
                print(f"Processing: {key}")

                # Download file to temporary location
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False
                ) as tmp_file:
                    s3_client.download_fileobj(bucket_name, key, tmp_file)
                    tmp_file_path = tmp_file.name

                try:
                    # Load PDF using PyMuPDFLoader
                    loader = PyMuPDFLoader(tmp_file_path)
                    pdf_docs = loader.load()

                    # Add source metadata
                    for doc in pdf_docs:
                        doc.metadata["source"] = f"s3://{bucket_name}/{key}"

                    documents.extend(pdf_docs)

                finally:
                    # Clean up temporary file
                    os.unlink(tmp_file_path)

    except Exception as e:
        print(f"Error loading PDFs from S3: {e}")
        raise

    return documents
