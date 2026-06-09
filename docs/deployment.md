# Deployment Guide

Use Streamlit Community Cloud for the public class URL. GitHub Pages cannot host this app because the assistant needs a Python runtime, Streamlit, Pinecone, and OpenAI secrets.

## Prerequisites

- GitHub repository: `mnsrhz/CA_Tax_Policy_Assistant`
- Branch: `main`
- App file: `app.py`
- Secrets copied from your local `.streamlit/secrets.toml`

## Deploy On Streamlit Community Cloud

1. Go to `https://share.streamlit.io`.
2. Sign in with GitHub.
3. Click `Create app`.
4. Choose `Yup, I have an app`.
5. Select:
   - Repository: `mnsrhz/CA_Tax_Policy_Assistant`
   - Branch: `main`
   - Main file path: `app.py`
6. Choose an app URL, such as `ca-tax-policy-assistant`.
7. Open advanced settings and paste the secrets below with your real values.
8. Click `Deploy`.

## Streamlit Secrets

Paste these into the Streamlit Cloud secrets editor. Do not commit real secrets to GitHub.

```toml
OPENAI_API_KEY = "replace-with-your-openai-key"
PINECONE_API_KEY = "replace-with-your-pinecone-key"
PINECONE_INDEX_NAME = "ca-tax-policy-assistant"
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"
```

## After Deployment

- Test a simple question first.
- Confirm the retrieval trace shows Vector, BM25, merged candidates, and reranked sources.
- Confirm source chips show readable titles instead of raw filenames.
- Share the generated `https://...streamlit.app` URL with your class.

## Updating The App

When you push changes to `main`, Streamlit Community Cloud redeploys the app automatically.

When you add or change PDFs:

1. Re-index Pinecone locally:

   ```bash
   python scripts/index_corpus.py
   ```

2. Commit and push the updated corpus and `data/bm25_index.json`.

3. Restart the Streamlit Cloud app if it does not refresh automatically.
