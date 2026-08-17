"""Vector store setup. Wraps Chroma so the rest of the app doesn't care
which backend we use — if we outgrow Chroma later we swap it here only."""

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from . import config


def _init_settings():
    """Point LlamaIndex at our chosen models + chunking strategy."""
    Settings.llm = OpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY)
    Settings.embed_model = OpenAIEmbedding(
        model=config.EMBED_MODEL, api_key=config.OPENAI_API_KEY
    )
    Settings.node_parser = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )


def get_index():
    """Return the index backed by the persisted Chroma collection.

    Creates the collection on first run, reuses it after that so we don't
    re-embed documents every time the app restarts.
    """
    _init_settings()

    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    collection = client.get_or_create_collection(config.COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )
    return index, collection
