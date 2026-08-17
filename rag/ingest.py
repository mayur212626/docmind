"""Load PDFs, split them into chunks, embed, and push into the vector store."""

from pathlib import Path

from llama_index.core import SimpleDirectoryReader

from .store import get_index


def ingest_files(file_paths):
    """Read the given PDF paths and add them to the index.

    Returns the number of chunks written so the UI can show progress.
    """
    docs = []
    for path in file_paths:
        # keep the filename on each doc so we can cite it later
        reader = SimpleDirectoryReader(input_files=[str(path)])
        loaded = reader.load_data()
        for d in loaded:
            d.metadata["source"] = Path(path).name
        docs.extend(loaded)

    index, _ = get_index()
    nodes = 0
    for doc in docs:
        index.insert(doc)
        nodes += 1

    return nodes


def collection_size():
    """How many chunks are currently stored. Lets the UI say 'ready' or not."""
    _, collection = get_index()
    return collection.count()
