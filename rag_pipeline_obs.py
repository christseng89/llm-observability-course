"""rag_pipeline_obs.py - Complete RAG Pipeline with Langfuse Observability

Required packages:
    pip install langfuse chromadb sentence-transformers anthropic langchain-core langchain-text-splitters python-dotenv
"""

import sys
from pathlib import Path
from typing import Any

import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv

# LangChain document format and text splitting
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from common import print_section
from langfuse import get_client, observe, propagate_attributes

load_dotenv()

PROJECT_NAME = "rag_pipeline_obs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # dim 384
MODEL = "claude-haiku-5-5"  # or "claude-sonnet-4-6" for more complex tasks

# Initialize chromadb with persistent storage
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection(
    name="documents", metadata={"hnsw:space": "cosine"}
)

# initialize embedding model once
embedding_model = SentenceTransformer(EMBEDDING_MODEL)


# =============================================================================
# DOCUMENT INDEXING PIPELINE
# =============================================================================
@observe
def rag_load_and_index_docs(docs_dir: str = "./docs") -> int:

    documents = rag_load_markdown_docs(docs_dir)
    if not documents:
        return 0

    chunks = rag_chunk_docs(documents)
    return rag_index_chunks(chunks)


@observe()
def rag_load_markdown_docs(docs_dir: str) -> list[Document]:
    """Load UTF-8 markdown files recursively into LangChain documents."""
    directory = Path(docs_dir)
    if not directory.exists():
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Docs path is not a directory: {docs_dir}")

    documents = [
        Document(
            page_content=path.read_text(encoding="utf-8"),
            metadata={"source": str(path)},
        )
        for path in sorted(directory.rglob("*.md"))
        if path.is_file()
        and not any(part.startswith(".") for part in path.relative_to(directory).parts)
    ]

    # Update current span with metadata (Langfuse SDK v4)
    get_client().update_current_span(
        metadata={"docs_loaded": len(documents), "docs_dir": docs_dir}
    )
    return documents


@observe()
def rag_chunk_docs(
    documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[Document]:
    """Split documents into smaller chunks for retrieval."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)

    get_client().update_current_span(
        metadata={"total_chunks": len(chunks), "chunk_size": chunk_size}
    )
    return chunks


# rag_index_chunks() does both:
# 1. Embedding: converts each chunk’s text into a numeric vector using embedding_model.encode().
# 2. Indexing: stores the vector, text, ID, and source metadata in ChromaDB using collection.upsert().
@observe()
def rag_index_chunks(chunks: list[Document]) -> int:
    """Create embeddings and store in ChromaDB."""
    ids, documents, metadatas, embeddings = [], [], [], []

    for i, chunk in enumerate(chunks):
        embedding = embedding_model.encode(chunk.page_content).tolist()
        ids.append(f"chunk_{i}")
        documents.append(chunk.page_content)
        metadatas.append({"source": chunk.metadata.get("source", "unknown")})
        embeddings.append(embedding)

    collection.upsert(
        ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
    )

    get_client().update_current_span(
        metadata={"chunks_indexed": len(chunks), "embedding_model": EMBEDDING_MODEL}
    )
    return len(chunks)


# =============================================================================
# RAG QUERY PIPELINE
# =============================================================================
@observe()
def rag_pipeline(query: str) -> str:
    """
    Complete RAG pipeline with full observability.
    Each step becomes a span in the trace.
    """
    query_embedding = rag_embed_query(query)
    chunks = rag_retrieve_chunks(query_embedding)
    context = rag_build_context(chunks)
    response = rag_response_claude(query, context)
    return response


@observe()
def rag_embed_query(query: str) -> list[float]:
    """Embed the user query."""
    embedding = embedding_model.encode(query).tolist()

    get_client().update_current_span(
        metadata={"query_length": len(query), "embedding_dim": len(embedding)}
    )
    return embedding


@observe()
def rag_retrieve_chunks(embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
    """Retrieve relevant document chunks from ChromaDB."""
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if results["documents"] and results["documents"][0]:
        for i in range(len(results["documents"][0])):
            chunks.append(
                {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

    get_client().update_current_span(
        metadata={
            "chunks_retrieved": len(chunks),
            "avg_distance": (
                sum(c["distance"] for c in chunks) / len(chunks) if chunks else 0
            ),
        }
    )
    return chunks


@observe()
def rag_build_context(chunks: list[dict[str, Any]]) -> str:
    """Assemble retrieved chunks into context string."""
    if not chunks:
        return "No relevant context found."

    context_parts = []
    for i, chunk in enumerate(chunks):
        source = chunk["metadata"].get("source", "unknown")
        context_parts.append(f"[Source {i + 1} - {source}]: {chunk['content']}")

    context = "\n\n".join(context_parts)

    get_client().update_current_span(
        metadata={"context_length": len(context), "num_chunks_used": len(chunks)}
    )
    return context


@observe()
def rag_response_claude(query: str, context: str) -> str:
    """Wrap a Claude generation in a span with token tracking."""
    client = Anthropic()

    prompt = f"""Use the following context to answer the question.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {query}

Answer:"""

    model = MODEL
    messages = [{"role": "user", "content": prompt}]
    with get_client().start_as_current_observation(
        as_type="generation",
        name="Claude-generation",
        model=model,
        input=messages,
        model_parameters={"max_tokens": 1024},
        metadata={"prompt_length": len(prompt)},
    ) as generation:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=messages,
        )
        content = "".join(
            block.text for block in response.content if block.type == "text"
        )
        generation.update(
            model=response.model,
            output=content,
            usage_details={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
        )
    return content


if __name__ == "__main__":
    print_section("Indexing documents from ./docs folder to RAG...")

    with propagate_attributes(
        user_id="user_123",
        tags=["observability", "rag_pipeline"],
        metadata={"project": PROJECT_NAME},
    ):
        # Step 1: Index documents (run once or when docs change)
        try:
            num_indexed = rag_load_and_index_docs("./docs")
            print(f"\033[32mIndexed {num_indexed} chunks\033[0m")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Create a 'docs' folder with .md files first.")
            sys.exit(1)

        # Step 2: Query the RAG pipeline
        print_section("Querying RAG pipeline...")

        query = "What is Llamaindex and how do I set up?"
        print(f"\033[32mQuery:\033[0m {query}")

        result = rag_pipeline(query)
        respose_preview = result.split("\n")[0]  # Show only the first line for brevity
        print(f"\n\033[33mRAG Response Preview:\033[0m\n{respose_preview}")
        # print(f"\n\033[32mResponse:\033[0m\n{result}")

        # Always flush in short-lived scripts
        get_client().flush()
