"""Answer questions against the stored documents, with source citations.

The important bit: if retrieval comes back weak, we say so instead of
letting the model make something up. That honesty is what makes this
usable for real company docs.
"""

from .store import get_index
from . import config

SYSTEM_PROMPT = (
    "You answer strictly from the provided context. "
    "If the context does not contain the answer, say you don't know. "
    "Never invent facts. Keep answers concise and cite the source."
)


def ask(question):
    """Run a question through retrieval + generation.

    Returns a dict with the answer text and the sources it leaned on.
    """
    index, _ = get_index()

    retriever = index.as_retriever(similarity_top_k=config.TOP_K)
    hits = retriever.retrieve(question)

    # guardrail: nothing relevant found -> don't hallucinate
    top_score = max((h.score or 0) for h in hits) if hits else 0
    if not hits or top_score < config.MIN_SCORE:
        return {
            "answer": "I couldn't find that in the uploaded documents.",
            "sources": [],
            "confident": False,
        }

    query_engine = index.as_query_engine(
        similarity_top_k=config.TOP_K,
        system_prompt=SYSTEM_PROMPT,
    )
    response = query_engine.query(question)

    sources = []
    for node in response.source_nodes:
        sources.append(
            {
                "source": node.metadata.get("source", "unknown"),
                "page": node.metadata.get("page_label", "?"),
                "score": round(node.score or 0, 3),
                "snippet": node.text[:280].strip(),
            }
        )

    return {
        "answer": str(response),
        "sources": sources,
        "confident": True,
    }
