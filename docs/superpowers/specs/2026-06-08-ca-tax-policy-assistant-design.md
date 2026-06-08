# California Tax Policy Assistant Design

## Goal

Build a GitHub-backed Streamlit application for a classroom-accessible California tax assistant. The app will answer user questions using retrieval augmented generation over the PDFs in `Data Corpus/`, with visible source citations, retrieval trace details, and lightweight filtering controls.

The public app will be hosted on Streamlit Community Cloud from a GitHub repository. GitHub Pages is not required because the app needs Python execution, model loading, Pinecone access, and OpenAI API calls.

## Current Inputs

- `Data Corpus/`: tax PDFs including California FTB documents and IRS publications.
- `UX Design/california_tax_assistant_ui.html`: chat-style UI mockup with sidebar, answer bubbles, source chips, retrieval trace, disclaimer, and suggested follow-up questions.

## Selected Stack

- UI and app runtime: Streamlit
- Deployment: Streamlit Community Cloud, connected to GitHub
- Vector database: Pinecone
- PDF extraction: PyMuPDF
- Chunking: structure-aware semantic chunking
- Embeddings: local `BAAI/bge-small-en-v1.5` through `sentence-transformers`
- Retrieval: Pinecone vector search with metadata filters
- Reranking: local lightweight reranker, initially `cross-encoder/ms-marco-MiniLM-L-6-v2` or `BAAI/bge-reranker-base`
- Answer generation: OpenAI API
- Secrets: Streamlit secrets for OpenAI and Pinecone credentials

The embedding model used for offline indexing and runtime query embedding must remain the same.

## Architecture

The project has two main flows.

### Offline Indexing Flow

1. Read PDFs from `Data Corpus/`.
2. Extract page-level text with source and page metadata.
3. Detect document metadata such as tax year, agency, jurisdiction, document type, and form/publication number.
4. Split pages into paragraphs and sections.
5. Group related adjacent text into semantic chunks while preserving page and section references.
6. Generate chunk embeddings locally with `BAAI/bge-small-en-v1.5`.
7. Upsert vectors and metadata into Pinecone.

The indexing script is run locally before deployment. The deployed Streamlit app will not re-index PDFs on normal startup.

### Runtime Question Answering Flow

1. User selects filters and asks a question in Streamlit.
2. App embeds the query with `BAAI/bge-small-en-v1.5`.
3. App builds a Pinecone metadata filter from the UI controls and inferred query hints.
4. Pinecone retrieves candidate chunks.
5. If strict filters return too few candidates, retrieval widens filters in a controlled fallback path.
6. Local reranker scores the retrieved candidates.
7. The top chunks are passed to OpenAI with citation and safety instructions.
8. Streamlit displays the answer, source citations, disclaimer, and retrieval trace.

## Metadata

Each chunk stored in Pinecone should include:

- `chunk_id`
- `source_file`
- `source_title`
- `page_number`
- `tax_year`
- `jurisdiction`: `federal`, `california`, or `mixed`
- `agency`: `IRS`, `FTB`, or `unknown`
- `document_type`: `publication`, `form`, `instructions`, `booklet`, or `unknown`
- `form_or_pub_number`
- `section_heading`
- `topic_tags`
- `text`

Metadata values should be normalized where possible so UI filters and Pinecone filters stay predictable.

## Metadata Filtering

The UI will expose visible controls:

- Tax year: dropdown, defaulting to `2024` when available
- Jurisdiction: segmented control for `California`, `Federal`, or `Both`
- Document type: dropdown or multiselect for `All`, `Forms`, `Instructions`, `Publications`, and `Booklets`
- Source scope: optional dropdown for `All sources`, `IRS only`, or `FTB only`

User-selected filters take precedence over inferred filters. Query inference can add hints such as agency, form/publication number, or topic only when confidence is high.

If strict metadata filters return too few candidates, the app will relax filters gradually and record that behavior in the retrieval trace. For example, the app may widen from `California` to `Both` for questions that require federal conformity context.

## Chunking

Chunking should be legal/tax aware rather than only fixed-size character splitting.

The chunker will:

- preserve page boundaries for citations
- detect headings and numbered subsections where possible
- split text into paragraphs or section-like blocks
- group adjacent blocks by semantic similarity
- avoid mixing unrelated tax topics in one chunk
- enforce a maximum size for retrieval and context usability
- optionally include a small overlap when a section spans boundaries

Semantic chunking should favor citation accuracy and topical coherence over producing perfectly uniform chunk sizes.

## Prompting And Answer Generation

The OpenAI prompt will instruct the model to:

- answer only from retrieved context
- cite source document and page for specific claims
- distinguish IRS/federal guidance from California FTB guidance
- state when the loaded documents do not support an answer
- avoid inventing thresholds, deadlines, form rules, or eligibility requirements
- include an informational disclaimer

The app should prefer concise, practical answers with enough explanation for a classroom user to see why the answer follows from the retrieved sources.

## Streamlit UX

The Streamlit UI should adapt the supplied HTML mockup:

- sidebar with app identity, new question action, and recent questions
- top area with active question title and status badges
- chat-style message area
- filter controls near the chat input or top of the conversation
- suggested follow-up chips
- source chips with document and page labels
- retrieval trace showing selected filters, candidate count, fallback widening, and reranked top chunks
- clear disclaimer in assistant responses

The interface should feel like a focused assistant, not a search form. Filters should be compact and easy to adjust.

## Proposed File Structure

```text
CA_Tax_Policy_Assistant/
  app.py
  requirements.txt
  .streamlit/
    config.toml
  src/
    config.py
    pdf_loader.py
    chunking.py
    embeddings.py
    pinecone_store.py
    retrieval.py
    reranking.py
    generation.py
    metadata.py
    ui.py
  scripts/
    index_corpus.py
  Data Corpus/
  UX Design/
```

Responsibilities:

- `app.py`: Streamlit entry point
- `scripts/index_corpus.py`: local corpus indexing script
- `src/pdf_loader.py`: page-level PDF extraction
- `src/chunking.py`: semantic chunk construction
- `src/metadata.py`: document and query metadata helpers
- `src/embeddings.py`: embedding model loading and text embedding
- `src/pinecone_store.py`: Pinecone connection, index setup, upsert, and search
- `src/retrieval.py`: filter construction, retrieval, and fallback widening
- `src/reranking.py`: local reranker loading and scoring
- `src/generation.py`: OpenAI prompt and answer generation
- `src/ui.py`: Streamlit layout and styling helpers

## Error Handling

- Missing API keys: show local setup guidance without exposing secrets.
- Pinecone unavailable: report retrieval service unavailable.
- OpenAI unavailable: display retrieved sources and explain that generation failed.
- Too few filtered results: widen filters and show the widening in the trace.
- Weak evidence: state that the loaded documents do not provide enough support.
- Slow model loading: cache embedding and reranker models with Streamlit caching.

## Testing Plan

- PDF extraction smoke test confirms every PDF yields text and page metadata.
- Chunking test confirms chunks have source, page, tax year, jurisdiction, and reasonable size.
- Embedding test confirms vector dimension matches the Pinecone index.
- Retrieval test confirms known questions return relevant chunks with metadata.
- Filter test confirms UI selections produce expected Pinecone filters.
- Reranking test confirms candidates are reordered and truncated.
- Generation test uses mocked context to confirm citation and disclaimer instructions are included.

## Deployment Notes

The GitHub repository will contain the Streamlit app code and indexing script. Streamlit Community Cloud will deploy `app.py` from the repository. Secrets will be configured in Streamlit Cloud, not committed to the repository.

Indexing is a separate local operation. If the corpus changes, rerun `scripts/index_corpus.py` locally to update Pinecone, then redeploy only if application code changed.

## Open Decisions For Implementation

- Choose final local reranker after a small performance check.
- Choose exact chunk size and similarity threshold after inspecting extracted PDF text.
- Decide whether chat history persists only in Streamlit session state or in a lightweight local/cloud store. For the first version, session state is sufficient.
