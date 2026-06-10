# UCLA Dining Ingestion & Chunking Pipeline

This directory contains the document ingestion, preprocessing, and fixed-size chunking implementation for the UCLA Dining RAG system (Milestone 3).

## Overview

The pipeline performs three main steps:

1. **Document Ingestion**: Load documents from 12 sources (Reddit, Google Maps, YouTube, BruinWalk, UCLA official dining)
2. **Preprocessing**: Normalize dining hall names, strip metadata, filter transactional posts
3. **Chunking**: Apply fixed-size token-based sliding window chunking (350 tokens, 50-token overlap)
4. **Save**: Output chunks to JSON with metadata (source, chunk_id, token_count)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For production scrapers, also install optional dependencies:
```bash
# For Reddit
pip install praw

# For web scraping
pip install requests beautifulsoup4

# For YouTube transcripts
pip install youtube-transcript-api

# For browser automation (if needed)
pip install selenium
```

### 2. Run with Sample Documents

```bash
python ingestion.py
```

This runs the pipeline with sample documents and outputs chunks to `documents/chunks.json`.

### 3. Run Tests

```bash
python test_ingestion.py
```

This runs a comprehensive test suite:
- ✓ Tokenization
- ✓ Fixed-size chunking
- ✓ Preprocessing (name normalization, metadata stripping, post filtering)
- ✓ Full pipeline
- ✓ Chunk quality metrics

## Pipeline Details

### Chunking Strategy

**Parameters:**
- **Chunk size**: 350 tokens (target range: 300–400)
- **Overlap**: 50 tokens (≈2–3 sentences, 12–15% of chunk)
- **Method**: Fixed-size token-based sliding window (no sentence boundary awareness)

**How it works:**
```
Tokens: [0---50---100---150---200---250---300---350---400---450...]
         |=========Chunk 1========|
                          |=========Chunk 2========|
                                               |=========Chunk 3========|
```

The window slides forward by `(chunk_size - overlap) = 300` tokens each iteration.

**Expected output:** ~300–500 chunks from 100 dining documents

### Preprocessing

**Operations applied (per-document):**

1. **Remove HTML/markup** - Strip `<tags>` if present
2. **Normalize dining hall names** - Map aliases:
   - "FEAST at Rieber" → "FEAST"
   - "Rieber dining" → "FEAST"
   - "De Neve Dining Hall" → "De Neve"
   - etc.
3. **Strip Reddit metadata** (if from Reddit):
   - Remove usernames (`u/username`)
   - Remove timestamps ("2 days ago")
   - Remove awards ("Gold", "Silver")
4. **Filter transactional posts** - Skip SWIPE trading posts
5. **Normalize whitespace** - Remove extra spaces/newlines

### Output Format

**File**: `documents/chunks.json`

**Structure**:
```json
{
  "metadata": {
    "total_chunks": 342,
    "chunk_size_tokens": 350,
    "overlap_tokens": 50,
    "chunking_method": "fixed-size token-based sliding window"
  },
  "chunks": [
    {
      "chunk_id": 0,
      "source": "https://www.reddit.com/r/ucla/search/?q=dining",
      "chunk_order": 0,
      "text": "FEAST at Rieber is one of the best...",
      "token_count": 287,
      "original_doc_length": 1450,
      "doc_index": 0
    },
    ...
  ]
}
```

**Metadata per chunk:**
- `chunk_id`: Unique chunk identifier (0, 1, 2, ...)
- `source`: Original document source URL
- `chunk_order`: Position within document (0 for first chunk, 1 for second, etc.)
- `text`: Chunk text content
- `token_count`: Number of tokens in this chunk
- `original_doc_length`: Length of original document before chunking
- `doc_index`: Index of source document

## Production Setup

### Currently Supported: Demo Mode

The default `load_sample_documents()` provides 8 example documents for testing. No additional setup required to test locally.

### Enable Production Scrapers

To fetch real documents from all 12 sources, follow setup guide in `scrapers.py`:

```bash
python scrapers.py
```

This prints setup instructions for each source.

#### 1. Reddit (r/UCLA, r/college, r/UCLAHousing)

**Setup:**
1. Create Reddit app: https://www.reddit.com/prefs/apps (log in with UCLA account)
2. Get credentials: `client_id`, `client_secret`, `user_agent`
3. Install: `pip install praw`
4. Add credentials to `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USER_AGENT=UCLA-Dining-RAG/1.0
   ```

**Why valuable**: Hundreds of real student opinions, diverse perspectives

#### 2. Google Maps Reviews

**Setup:**
1. Get API key: https://cloud.google.com/maps-platform
2. Enable Places API
3. Install: `pip install google-maps`
4. Note: Reviews require special handling (often anti-scraped)

**Why valuable**: Star ratings, aggregated reviews from multiple dining halls

#### 3. YouTube Transcripts

**Setup:**
1. Install: `pip install youtube-transcript-api`
2. Use YouTube Data API for search (requires API key)
3. Extract video IDs from search results

**Why valuable**: Video reviews, long-form opinions, tone/emotion context

#### 4. BruinWalk Housing Guides

**Setup:**
1. Install: `pip install beautifulsoup4 requests`
2. Parse bruinwalk.com housing pages
3. Extract sections mentioning dining

**Why valuable**: Housing-specific dining context, resident reviews

#### 5. UCLA Dining Website

**Setup:**
1. Parse dining.ucla.edu menu pages
2. Extract dining hall descriptions, hours

**Why valuable**: Official information, menu context, verification source

## Usage

### Basic Pipeline (with sample docs)

```python
from ingestion import run_ingestion_pipeline

# Run entire pipeline
output_file, chunks = run_ingestion_pipeline()

print(f"Generated {len(chunks)} chunks")
print(f"Saved to: {output_file}")
```

### Custom Documents

```python
from ingestion import chunk_documents, save_chunks_to_json

documents = [
    {
        "text": "Your document text here",
        "source": "https://example.com"
    },
    ...
]

chunks = chunk_documents(documents, chunk_size=350, overlap=50)
output_file = save_chunks_to_json(chunks)
```

### Manual Verification

```python
from ingestion import verify_chunks
import json

# Load chunks
with open("documents/chunks.json") as f:
    data = json.load(f)
chunks = data["chunks"]

# Verify 10 random samples
verify_chunks(chunks, sample_size=10)
```

## Verification Checklist

After running the pipeline, manually verify:

- [ ] ~300–500 chunks generated (for 100 documents)
- [ ] Most chunks are 300–400 tokens
- [ ] No single review split across 3+ chunks
- [ ] Overlap regions repeat 2–3 sentences
- [ ] Chunks properly tagged with source
- [ ] Transactional posts filtered out
- [ ] Dining hall names normalized

Run `test_ingestion.py` to automate most of these checks:

```bash
python test_ingestion.py
```

Expected output:
```
TEST: Full Ingestion Pipeline
Generated X chunks
✓ Quality test passed (Y/Z chunks in target range)
✓ ALL TESTS PASSED
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'tiktoken'`
**Solution**: `pip install tiktoken`

### Issue: `AttributeError: 'NoneType' has no attribute 'encode'`
**Solution**: Tiktoken failed to load; using fallback tokenization (word-based). Install tiktoken or check OpenAI account status.

### Issue: Chunks are too small or too large
**Check**: Verify `chunk_size_tokens` and `overlap_tokens` parameters. Default is 350 tokens with 50-token overlap. Adjust as needed:
```python
chunks = chunk_documents(documents, chunk_size=400, overlap=60)
```

### Issue: Many transactional posts not filtered
**Check**: Regex patterns in `filter_transactional_posts()` may not match all variations. Add new patterns as needed.

## Next Steps

After verifying chunks:

1. **Milestone 4**: Embedding & Vector Store
   - Embed chunks using `sentence-transformers/all-MiniLM-L6-v2`
   - Store in FAISS
   - Build retrieval function (top-k=6)

2. **Milestone 5**: Grounded Generation
   - Build system prompt enforcing grounding
   - Implement LLM wrapper with retrieval
   - Evaluate on 5 test questions

See main `planning.md` for full specification.

## File Reference

| File | Purpose |
|------|---------|
| `ingestion.py` | Main pipeline: tokenization, preprocessing, chunking, JSON output |
| `scrapers.py` | Web scrapers for 12 sources (with setup guide) |
| `test_ingestion.py` | Test suite for all components |
| `documents/chunks.json` | Output: chunks with metadata |
| `requirements.txt` | Dependencies (tiktoken + optional scrapers) |

## Performance Notes

- **Tokenization**: ~1 second per 100KB of text (with tiktoken)
- **Chunking**: ~0.1 second per 100 chunks
- **Memory**: ~50MB for 5000 chunks (rough estimate)

For 100 dining documents (~1-2MB total):
- Expected runtime: <5 seconds
- Output size: ~500KB JSON file

---

For questions or issues, refer to `planning.md` or run `python test_ingestion.py` for diagnostic output.
