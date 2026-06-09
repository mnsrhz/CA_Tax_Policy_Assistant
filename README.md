# California Tax Policy Assistant

A Streamlit-based tax assistant that uses retrieval augmented generation over a curated corpus of California FTB and IRS tax documents. The app is designed for classroom use and will provide cited, source-grounded answers with metadata filtering, retrieval traces, and a tax-professional disclaimer.

## Project Status

Initial implementation is available on the feature branch. The app can run locally, and the indexing script is ready to use once Pinecone and OpenAI secrets are configured.

The current design spec is here:

```text
docs/superpowers/specs/2026-06-08-ca-tax-policy-assistant-design.md
```

## Tech Stack

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
app.py            Streamlit app entry point
Data Corpus/      Tax PDFs used as the RAG corpus
scripts/          Offline corpus indexing script
src/              RAG pipeline modules
tests/            Pytest test suite
UX Design/        HTML mockup for the intended assistant UI
docs/             Design documentation and implementation specs
```

## RAG Flow

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
PINECONE_CLOUD
PINECONE_REGION
```

`PINECONE_CLOUD` defaults to `aws` and `PINECONE_REGION` defaults to `us-east-1` when omitted.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Local Secrets

For local Streamlit runs, create `.streamlit/secrets.toml` or export environment variables before running the app.

Example `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "..."
PINECONE_API_KEY = "..."
PINECONE_INDEX_NAME = "..."
```

Environment variable alternative:

```bash
export OPENAI_API_KEY="..."
export PINECONE_API_KEY="..."
export PINECONE_INDEX_NAME="..."
```

## Run Tests

```bash
pytest -v
```

## Indexing The Corpus

Create the Pinecone index before indexing the corpus:

```bash
python scripts/setup_pinecone_index.py
```

The index is created as a serverless cosine index with `384` dimensions for `BAAI/bge-small-en-v1.5`.

Run the indexing script locally after the Pinecone index exists:

```bash
python scripts/index_corpus.py
```

The deployed Streamlit app should not re-index the PDFs on normal startup.

## Run The App

```bash
streamlit run app.py
```

If secrets are missing, the app displays a setup warning instead of calling Pinecone or OpenAI.

## Deployment

Deploy through Streamlit Community Cloud from the GitHub repository. Streamlit Cloud should run `app.py` and use configured secrets for OpenAI and Pinecone access.

## Safety Notice

This project is for educational use. Generated responses should be treated as informational only and not as a substitute for advice from a licensed tax professional.
