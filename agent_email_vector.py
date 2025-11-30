import uuid

from email_reply_parser import EmailReplyParser
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Import configuration
from config import config

# from talon.signature import extract as extract_signature

embeddings = OllamaEmbeddings(
    model=config.OLLAMA_EMBEDDING_MODEL,
    base_url=config.OLLAMA_BASE_URL,
)


def clean_email(email):
    body = email["body"]

    # 1. Remove reply chain
    body = EmailReplyParser.parse_reply(body)

    # 2. Remove signature
    # body, sig = extract_signature(body)

    # 3. Normalize
    body = body.strip()

    combined = (
        f"Sender: {email['sender']}\n"
        f"Subject: {email['subject']}\n"
        f"Date: {email['date']}\n\n"
        f"{body}"
    )

    return combined


def build_vector_store(email_list, persist_directory=None):
    """
    Build a ChromaDB vector store from a list of email dictionaries.

    Args:
        email_list: List of email dictionaries with keys: sender, subject, date, body
        persist_directory: Directory to persist the vector store (uses config if not provided)

    Returns:
        ChromaDB vector store instance

    Raises:
        ValueError: If email_list is empty or invalid
        Exception: If vector store creation fails
    """
    if not email_list:
        raise ValueError("Email list cannot be empty")

    persist_dir = persist_directory or config.CHROMA_PERSIST_DIRECTORY

    try:
        cleaned_texts = []
        metadatas = []

        for e in email_list:
            # Validate email structure
            if not all(key in e for key in ["sender", "subject", "date", "body"]):
                raise ValueError(
                    f"Invalid email structure. Required keys: sender, subject, date, body"
                )

            cleaned = clean_email(e)
            cleaned_texts.append(cleaned)
            metadatas.append(
                {
                    "sender": e["sender"],
                    "subject": e["subject"],
                    "date": e["date"],
                    "id": str(uuid.uuid4()),
                }
            )

        vectorstore = Chroma.from_texts(
            texts=cleaned_texts,
            embedding=embeddings,
            metadatas=metadatas,
            collection_name=config.CHROMA_COLLECTION_NAME,
            persist_directory=persist_dir,
        )
        return vectorstore

    except Exception as e:
        raise Exception(f"Failed to build vector store: {e}")
