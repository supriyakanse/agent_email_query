import os

from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Import configuration
from config import config

# Initialize embeddings (same as in agent_email_vector.py)
embeddings = OllamaEmbeddings(
    model=config.OLLAMA_EMBEDDING_MODEL,
    base_url=config.OLLAMA_BASE_URL,
)

# Initialize LLM
llm = ChatOllama(
    model=config.OLLAMA_LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
    base_url=config.OLLAMA_BASE_URL,
)

# Define the custom prompt for the QA part of the chain
CUSTOM_PROMPT_TEMPLATE = """You are an intelligent email assistant. Answer the user's question based ONLY on the provided chat history and the retrieved email context.
Be concise, accurate, and helpful. If the context doesn't contain enough information to answer the question, state that you don't have enough information from the emails, but try to use the chat history to provide a conversational answer if possible.

Chat History:
{chat_history}

Retrieved Email Context:
{context}

Question: {question}

Answer:"""


def load_vector_store(persist_directory=None):
    """
    Load the existing ChromaDB vector store from disk.

    Args:
        persist_directory: Directory where ChromaDB data is stored (uses config if not provided)

    Returns:
        Loaded Chroma vectorstore instance

    Raises:
        FileNotFoundError: If vector store doesn't exist
    """
    persist_dir = persist_directory or config.CHROMA_PERSIST_DIRECTORY

    # Check if vector store exists
    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"Vector store not found at '{persist_dir}'. "
            "Please run the workflow to fetch and index emails first."
        )

    try:
        vectorstore = Chroma(
            collection_name=config.CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        return vectorstore
    except Exception as e:
        raise Exception(f"Failed to load vector store: {e}")


def create_conversational_query_chain(vectorstore):
    """
    Create a ConversationalRetrievalChain with memory for querying emails.

    Args:
        vectorstore: ChromaDB vector store instance

    Returns:
        ConversationalRetrievalChain instance
    """
    # Create a memory buffer to store chat history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,  # Important for some LLMs/chains
        output_key='answer'
    )

    # Create the retriever from the vectorstore
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": config.DEFAULT_RETRIEVAL_COUNT}
    )
    
    # Create the prompt template for the final QA step
    qa_prompt = ChatPromptTemplate.from_template(CUSTOM_PROMPT_TEMPLATE)

    # Create the ConversationalRetrievalChain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=False,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
    )

    return qa_chain


def query_emails(qa_chain, user_query):
    """
    Query the email vector store using the created conversational chain.

    Args:
        qa_chain: The ConversationalRetrievalChain instance
        user_query: User's question about emails

    Returns:
        Natural language response from the LLM
    """
    try:
        # The chain handles everything: history, retrieval, and generation
        result = qa_chain.invoke({"question": user_query})
        return result['answer']

    except Exception as e:
        raise Exception(f"Failed to query emails: {e}")


if __name__ == "__main__":
    try:
        # Load the vector store
        print("Loading vector store...")
        vectorstore = load_vector_store()
        
        # Create the conversational chain
        qa_chain = create_conversational_query_chain(vectorstore)

        # Get collection count
        count = vectorstore._collection.count()
        print(f"✓ Vector store loaded successfully")
        print(f"✓ Total emails in store: {count}")
        print("\n" + "=" * 50)

        # Example queries
        example_queries = [
            "How many emails did I receive?",
            "Who sent me the email about the project deadline?",
            "What was the subject of the email from that sender?",
        ]

        print("Example queries you can try:")
        for i, q in enumerate(example_queries, 1):
            print(f"  {i}. {q}")

        print("=" * 50 + "\n")

        # Interactive query loop
        while True:
            user_input = input(
                "Ask a question about your emails (or 'quit' to exit): "
            ).strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\nSearching and generating response...\n")
            try:
                response = query_emails(qa_chain, user_input)
                print(f"Answer: {response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

            print("-" * 50 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\nPlease run the email workflow first to fetch and index emails.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Failed to load vector store: {e}")
        exit(1)