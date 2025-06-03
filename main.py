"""
FDA Regulatory Assistant - Chainlit Application

This application provides an AI-powered assistant for FDA regulatory compliance
using LangGraph agents and RAG chains for cybersecurity and regulatory guidance.

Features:
- Question answering for FDA regulations and cybersecurity
- Gap analysis of regulatory submission documents
- ZIP file upload and processing
- Streaming responses with real-time progress updates
"""

import chainlit as cl
from ragchains.chain_manager import get_chain_manager
from graph.graph import process_user_request
from utils.document_parsers import extract_text_with_metadata
from typing import List, Dict, Any
import zipfile
import io
import os

# Get the global chain manager instance
chain_manager = get_chain_manager()

# Optional: Pre-warm chains at startup
# This will load both chains when the application starts
async def prewarm_chains():
    """Pre-warm both RAG chains at application startup (optional)"""
    await chain_manager.prewarm_chains()


# =============================================================================
# File Processing Functions
# =============================================================================


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text content from uploaded files using the document parser.

    Supports various file formats including text files, PDFs, and Word documents.
    Uses PyMuPDF for PDF parsing and python-docx for Word documents.

    Args:
        file_content: Raw file content as bytes
        filename: Name of the file for format detection

    Returns:
        Extracted text content as string
    """
    try:
        # Use the new document parser
        result = extract_text_with_metadata(file_content, filename)
        return result["text"]

    except Exception as e:
        return f"[Error extracting content from {filename}: {str(e)}]"


def process_zip_file(zip_content: bytes) -> List[Dict[str, Any]]:
    """
    Process uploaded ZIP file and extract documents.

    Args:
        zip_content: Raw ZIP file content

    Returns:
        List of extracted file data
    """
    files_data = []

    try:
        # Verify it's actually a ZIP file by checking magic bytes
        if len(zip_content) < 4:
            raise ValueError("File too small to be a valid ZIP file")

        # Check ZIP file magic bytes - ZIP files start with PK (0x504B)
        magic_bytes = zip_content[:4]
        if not (magic_bytes[:2] == b"PK"):
            raise ValueError(
                f"File does not appear to be a ZIP file. Magic bytes: {magic_bytes.hex()}"
            )

        with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zip_file:
            for file_info in zip_file.filelist:
                if not file_info.is_dir():
                    try:
                        file_content = zip_file.read(file_info.filename)
                        text_content = extract_text_from_file(
                            file_content, file_info.filename
                        )

                        files_data.append(
                            {
                                "name": file_info.filename,
                                "content": text_content,
                                "type": os.path.splitext(file_info.filename)[1].lower(),
                                "size": file_info.file_size,
                            }
                        )
                    except Exception as e:
                        files_data.append(
                            {
                                "name": file_info.filename,
                                "content": f"[Error processing file: {str(e)}]",
                                "type": "error",
                                "size": 0,
                            }
                        )

    except zipfile.BadZipFile as e:
        error_msg = f"Invalid ZIP file format: {str(e)}"
        files_data.append(
            {
                "name": "zip_format_error.txt",
                "content": error_msg,
                "type": "error",
                "size": 0,
            }
        )
    except Exception as e:
        error_msg = f"Error processing ZIP file: {str(e)}"
        files_data.append(
            {"name": "zip_error.txt", "content": error_msg, "type": "error", "size": 0}
        )

    return files_data


# =============================================================================
# Chainlit Event Handlers
# =============================================================================


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with the LangGraph workflow."""

    # Show loading message while initializing
    loading_msg = cl.Message(content="🔄 Initializing your FDA Regulatory Assistant...")
    await loading_msg.send()

    try:
        # Pre-warm RAG chains if not already done
        await chain_manager.prewarm_chains()

        # Set unified welcome message
        welcome_message = """Hello! I'm your **FDA Regulatory Assistant** powered by LangGraph agents.

I can help you with:
📋 **510K submissions** and regulatory guidance
🔒 **Cybersecurity requirements** for medical devices
📊 **Gap analysis** of submission documents
📄 **Compliance reports** and recommendations

**Two ways to get help:**
1. **Ask a question** about FDA regulations or cybersecurity
2. **Upload a ZIP file** containing your regulatory documents for comprehensive gap analysis

My specialist team includes:
- 🔒 **Cybersecurity Specialist** - FDA cybersecurity guidance and SOUP documentation
- 📋 **Regulatory Affairs Expert** - 510K, PMA, and regulatory compliance
- 🔍 **Compliance Auditor** - Gap analysis and readiness assessment
- 📄 **Report Generator** - Comprehensive reports and recommendations

How can I assist you today?"""

        # Update the loading message with the welcome message
        loading_msg.content = welcome_message
        await loading_msg.update()

    except Exception as e:
        error_message = f"❌ Sorry, there was an error initializing your assistant: {str(e)}. Please refresh and try again."
        loading_msg.content = error_message
        await loading_msg.update()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages with LangGraph workflow."""

    # Check for file attachments
    uploaded_files = []

    if message.elements:
        for element in message.elements:
            try:
                # Try different ways to access file content
                file_content = None
                file_name = None

                # Method 1: Direct attributes (content in memory)
                if (
                    hasattr(element, "content")
                    and element.content is not None
                    and hasattr(element, "name")
                ):
                    file_content = element.content
                    file_name = element.name
                # Method 2: Path-based (file saved to disk)
                elif (
                    hasattr(element, "path")
                    and element.path
                    and hasattr(element, "name")
                ):
                    try:
                        with open(element.path, "rb") as f:
                            file_content = f.read()
                        file_name = element.name
                    except Exception:
                        continue
                # Method 3: Alternative content access methods
                elif hasattr(element, "name"):
                    if hasattr(element, "bytes"):
                        file_content = element.bytes
                        file_name = element.name
                    elif hasattr(element, "data"):
                        file_content = element.data
                        file_name = element.name
                # Method 4: Skip URL-based elements
                elif hasattr(element, "url") and hasattr(element, "name"):
                    continue

                if file_content and file_name:
                    # Handle ZIP files for gap analysis
                    if file_name.lower().endswith(".zip"):
                        files_data = process_zip_file(file_content)
                        uploaded_files.extend(files_data)
                    else:
                        # Handle individual files
                        text_content = extract_text_from_file(file_content, file_name)
                        uploaded_files.append(
                            {
                                "name": file_name,
                                "content": text_content,
                                "type": os.path.splitext(file_name)[1].lower(),
                                "size": len(file_content),
                            }
                        )

            except Exception as e:
                # Add error file to show what went wrong
                uploaded_files.append(
                    {
                        "name": "file_processing_error.txt",
                        "content": f"Error processing uploaded file: {str(e)}",
                        "type": "error",
                        "size": 0,
                    }
                )

    # Create a new message to stream the response
    msg = cl.Message(content="")

    try:
        # Process the request with LangGraph workflow
        async for chunk in process_user_request(
            user_input=message.content,
            uploaded_files=uploaded_files if uploaded_files else None,
        ):
            await msg.stream_token(chunk)

    except Exception as e:
        error_msg = f"❌ Sorry, there was an error processing your request: {str(e)}"
        await msg.stream_token(error_msg)

    # Send the final message
    await msg.send()
