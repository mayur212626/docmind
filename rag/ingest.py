"""Load PDFs, split them into chunks, embed, and push into the vector store.

We extract text with pypdf a page at a time rather than leaning on a generic
directory reader — that way every chunk carries its real source file and page
number, which is what makes the citations trustworthy.
"""

from pathlib import Path

from llama_index.core import Document
from pypdf import PdfReader

from .store import get_index


def ingest_files(file_paths):
    """Read the given PDF paths and add them to the index.

    Returns the number of pages written so the UI can show progress.
    """
    docs = []
    for path in file_paths:
        name = Path(path).name
        reader = PdfReader(str(path))
        for page_num, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue  # skip blank / image-only pages
            docs.append(
                Document(
                    text=text,
                    metadata={"source": name, "page_label": str(page_num)},
                )
            )

    index, _ = get_index()
    for doc in docs:
        index.insert(doc)

    return len(docs)


def collection_size():
    """How many chunks are currently stored. Lets the UI say 'ready' or not."""
    _, collection = get_index()
    return collection.count()
