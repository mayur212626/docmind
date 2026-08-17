"""DocMind — chat with your documents.

Upload PDFs, ask questions, get answers with the exact source passages
they came from. Built to cut down the time teams spend digging through
policy docs, manuals, and handbooks.
"""

import tempfile
from pathlib import Path

import streamlit as st

from rag.ingest import ingest_files, collection_size
from rag.query import ask

st.set_page_config(page_title="DocMind", page_icon="📄", layout="wide")

st.title("DocMind")
st.caption("Ask questions across your documents. Answers come with sources.")


# ---- sidebar: upload + index status ----
with st.sidebar:
    st.header("Documents")

    uploaded = st.file_uploader(
        "Upload PDFs", type=["pdf"], accept_multiple_files=True
    )

    if uploaded and st.button("Add to knowledge base", type="primary"):
        tmp_paths = []
        for f in uploaded:
            tmp = Path(tempfile.gettempdir()) / f.name
            tmp.write_bytes(f.getbuffer())
            tmp_paths.append(tmp)

        with st.spinner(f"Indexing {len(tmp_paths)} file(s)..."):
            added = ingest_files(tmp_paths)
        st.success(f"Added {added} document section(s).")

    try:
        count = collection_size()
    except Exception:
        count = 0
    st.metric("Chunks indexed", count)


# ---- main: chat ----
def _render_sources(sources):
    with st.expander("Sources"):
        for s in sources:
            st.markdown(
                f"**{s['source']}** — page {s['page']} "
                f"(match {s['score']})"
            )
            st.caption(s["snippet"])


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            _render_sources(msg["sources"])


prompt = st.chat_input("Ask something about your documents...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            result = ask(prompt)
        st.markdown(result["answer"])
        if result["sources"]:
            _render_sources(result["sources"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )
