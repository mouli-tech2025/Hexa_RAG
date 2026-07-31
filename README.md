# SafeRAG

**SafeRAG** is a privacy-first, offline Retrieval-Augmented Generation (RAG) system for intelligent document search and question answering. It combines efficient open-source AI models with a production-grade vector database to provide fast, accurate, and secure document intelligence without relying on cloud APIs or external LLM services.

---

## Overview

SafeRAG enables users to upload documents, perform semantic search, and receive precise answers from their data while keeping all processing local. The system is designed for environments where privacy, low latency, and offline capability are essential.

The pipeline consists of document parsing, semantic embedding generation, vector search, passage reranking, and extractive question answering.

---

## Key Features

- Fully offline document processing
- Privacy-first architecture
- Semantic search using vector embeddings
- OCR support for scanned documents
- Multi-format document support
- Fast similarity search with Actian Vector Database
- Intelligent passage reranking
- Accurate extractive question answering
- Modular and lightweight architecture

---

## Supported File Types

- PDF
- DOCX
- TXT
- PNG
- JPG

---

## System Architecture

```text
                     Documents
                         │
                         ▼
                 Docling Parser
          (OCR + Layout + Tables)
                         │
                         ▼
                  Document Chunking
                         │
                         ▼
            EmbeddingGemma-300M
            (Vector Embeddings)
                         │
                         ▼
             Actian Vector Database
                         ▲
                         │
                    User Query
                         │
                         ▼
            EmbeddingGemma-300M
              (Query Embedding)
                         │
                         ▼
                Similarity Search
                         │
                         ▼
             Qwen3 Reranker-0.6B
                         │
                         ▼
             RoBERTa SQuAD2 QA
                         │
                         ▼
                  Final Answer
```

---

## Technology Stack

### Programming Language

- Python
- TypeScript
- JavaScript

### AI Models

- Docling
- EmbeddingGemma-300M
- Qwen3 Reranker-0.6B
- RoBERTa SQuAD2

### Vector Database

- Actian Vector Database

### Core Libraries

- Hugging Face Transformers
- PyTorch
- Sentence Transformers
- Docling
  

---

## AI Pipeline

### Docling

Responsible for parsing and preprocessing documents.

Capabilities include:

- PDF parsing
- OCR
- Table extraction
- Layout analysis
- Metadata extraction

### EmbeddingGemma-300M

Generates dense vector embeddings for:

- Document chunks
- User queries

These embeddings enable semantic similarity search within the vector database.

### Actian Vector Database

Stores document embeddings and performs high-performance vector similarity search.

Key advantages include:

- Production-ready architecture
- Fast vector retrieval
- Offline deployment
- Scalable indexing

### Qwen3 Reranker-0.6B

Improves retrieval quality by reranking retrieved passages according to their relevance to the user's query.

### RoBERTa SQuAD2

Extractive question answering model responsible for identifying the exact answer span from the retrieved context.

---

## Workflow

1. Upload one or more documents.
2. Parse documents using Docling.
3. Perform OCR when necessary.
4. Split documents into semantic chunks.
5. Generate embeddings using EmbeddingGemma-300M.
6. Store embeddings in Actian Vector Database.
7. Convert the user query into an embedding.
8. Retrieve the most relevant document chunks.
9. Rerank retrieved passages using Qwen3 Reranker.
10. Extract the final answer using RoBERTa SQuAD2.
11. Return the response to the user.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/SafeRAG.git
cd SafeRAG
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application


---

## License

This project is licensed under the MIT License.
