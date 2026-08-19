"""End-to-end check of the RAG pipeline against the sample handbook.

Calls the model and embeddings API, so it needs OPENAI_API_KEY (in .env or
the environment). Uses a throwaway vector store so it never touches your real
index.

    python tests/test_rag_live.py
"""

import os
import tempfile

from dotenv import load_dotenv

load_dotenv()

# point the vector store at a temp dir BEFORE importing the rag package, so
# the test starts from an empty index and cleans up after itself
os.environ["CHROMA_DIR"] = tempfile.mkdtemp(prefix="docmind_test_")

from rag.ingest import ingest_files, collection_size  # noqa: E402
from rag.query import ask  # noqa: E402

SAMPLE_PDF = "sample_data/employee_handbook.pdf"


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping live test: OPENAI_API_KEY not set.")
        return

    print("Ingesting sample handbook...")
    ingest_files([SAMPLE_PDF])
    print("Chunks indexed:", collection_size(), "\n")

    # 1) a fact that IS in the document
    q1 = "How many days of paid annual leave do full-time employees get?"
    r1 = ask(q1)
    print("Q:", q1)
    print("A:", r1["answer"])
    print("Sources:", [s["source"] for s in r1["sources"]])
    assert "21" in r1["answer"], "expected the answer to contain '21'"
    assert r1["sources"], "expected at least one cited source"
    print("-> fact lookup OK\n")

    # 2) the honesty guardrail: something NOT in the document
    q2 = "What is the company's parental leave policy?"
    r2 = ask(q2)
    print("Q:", q2)
    print("A:", r2["answer"])
    # it should decline rather than invent a policy — accept either the
    # retrieval-level refusal or a natural "not in the document" answer
    ans = r2["answer"].lower()
    refusal_markers = [
        "couldn't find", "could not find", "don't know", "do not know",
        "not include", "does not include", "no information", "not mentioned",
        "not specified", "not provided", "not contain",
    ]
    declined = (not r2["confident"]) or any(m in ans for m in refusal_markers)
    assert declined, f"expected a refusal, got: {r2['answer']}"
    print("-> guardrail OK\n")

    print("All live RAG checks passed.")


if __name__ == "__main__":
    main()
