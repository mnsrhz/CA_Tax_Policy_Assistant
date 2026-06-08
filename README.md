# California Tax Policy Assistant

A Streamlit-based tax assistant that uses retrieval augmented generation over a curated corpus of California FTB and IRS tax documents. The app is designed for classroom use and will provide cited, source-grounded answers with metadata filtering, retrieval traces, and a tax-professional disclaimer.

## Project Status

Design approved. Implementation is planned but not yet built.

The current design spec is here:

```text
docs/superpowers/specs/2026-06-08-ca-tax-policy-assistant-design.md
```

## Planned Tech Stack

- Streamlit for the web app
- Streamlit Community Cloud for public GitHub-backed deployment
- Pinecone for vector search
- PyMuPDF for PDF extraction
- Structure-aware semantic chunking for tax/legal documents
- `BAAI/bge-small-en-v1.5` for local/free embeddings
- Local lightweight reranking
- OpenAI API for final answer generation

## Repository Contents

```text
Data Corpus/      Tax PDFs used as the RAG corpus
UX Design/        HTML mockup for the intended assistant UI
docs/             Design documentation and implementation specs
```

## Planned RAG Flow

```text
PDFs
  -> page-level text extraction
  -> semantic chunking with metadata
  -> local embeddings
  -> Pinecone upsert
  -> filtered vector retrieval
  -> local reranking
  -> OpenAI answer generation
  -> cited Streamlit response
```

## Metadata Filtering

The app will include visible controls for:

- Tax year
- Jurisdiction: California, Federal, or Both
- Document type
- Source scope: IRS, FTB, or All sources

These controls will be converted into Pinecone metadata filters before retrieval. If filters are too narrow, the app will widen them in a controlled fallback path and show that behavior in the retrieval trace.

## Required Secrets

Secrets should not be committed to GitHub. For local development, use environment variables or a local Streamlit secrets file. For deployment, configure secrets in Streamlit Community Cloud.

Expected secrets:

```text
OPENAI_API_KEY
PINECONE_API_KEY
PINECONE_INDEX_NAME
```

Additional Pinecone settings may be added during implementation, such as cloud and region values.

## Local Development

Implementation steps will be added once the app skeleton is created. The expected commands will look like:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Indexing The Corpus

Corpus indexing will be handled by a local script once implementation begins:

```bash
python scripts/index_corpus.py
```

The deployed Streamlit app should not re-index the PDFs on normal startup.

## Deployment

The app will be deployed through Streamlit Community Cloud from the GitHub repository. Streamlit Cloud will run `app.py` and use configured secrets for OpenAI and Pinecone access.

## Safety Notice

This project is for educational use. Generated responses should be treated as informational only and not as a substitute for advice from a licensed tax professional.

