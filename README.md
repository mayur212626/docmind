# DocMind

Chat with your documents. Upload PDFs, ask questions in plain English, and
get answers backed by the exact passages they came from — with the source
file and page shown for every answer.

Built for teams that waste hours digging through policy documents, manuals,
handbooks, and contracts.

## Why it's different

Most document chatbots happily make things up when they can't find an answer.
DocMind checks how well the retrieved passages actually match the question,
and if the match is weak it says *"I couldn't find that in the uploaded
documents"* instead of guessing. For real company docs, that honesty matters
more than a confident wrong answer.

## Stack

- **Retrieval:** LlamaIndex
- **Vector store:** ChromaDB (local, persisted)
- **Embeddings + LLM:** OpenAI
- **UI:** Streamlit

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then add your OpenAI key
```

## Run

```bash
streamlit run app.py
```

Upload a few PDFs from the sidebar, wait for indexing, then ask away.

## How it works

1. PDFs are split into overlapping chunks and embedded.
2. Embeddings are stored in Chroma and persisted to disk, so restarts don't
   re-embed everything.
3. A question retrieves the closest chunks; if the best match is too weak the
   answer is refused rather than hallucinated.
4. Good matches are passed to the model, which answers and cites its sources.

## Roadmap

- Redis cache for repeated questions
- Swap Chroma for a hosted vector DB at scale
- Support DOCX and web pages, not just PDFs
- Answer-quality logging
