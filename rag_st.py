import streamlit as st
from typing import List
from docx import Document
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="RAG Document QA", layout="wide")
st.title("📄 RAG Document QA")

@st.cache_data
def load_docx(file) -> List[str]:
    doc = Document(file)
    text = " ".join(p.text for p in doc.paragraphs if p.text.strip())

    sentences = text.split(".")
    chunks, buffer = [], ""

    for s in sentences:
        buffer += s.strip() + ". "
        if len(buffer.split()) >= 40:
            chunks.append(buffer.strip())
            buffer = ""

    if buffer:
        chunks.append(buffer.strip())

    return chunks

def retrieve(query: str, docs: List[str], top_k: int = 3) -> List[str]:
    if not docs:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    doc_vectors = vectorizer.fit_transform(docs)
    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(query_vector, doc_vectors)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [docs[i] for i in top_indices if scores[i] > 0]

uploaded_file = st.file_uploader("Upload DOCX file", type=["docx"])
query = st.text_input("Ask a question")
top_k = st.select_slider("Top-K Results", options=[1, 2, 3, 5], value=3)

if st.button("Search"):
    if not uploaded_file:
        st.warning("Please upload a DOCX file")
    elif not query.strip():
        st.warning("Please enter a question")
    else:
        docs = load_docx(uploaded_file)
        results = retrieve(query, docs, top_k)

        if not results:
            st.info("No relevant answers found.")
        else:
            for i, r in enumerate(results, 1):
                st.markdown(f"**Answer {i}:** {r}")
