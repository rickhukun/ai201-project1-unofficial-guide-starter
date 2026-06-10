"""
Document ingestion pipeline for UCLA dining RAG system.
Scrapes/downloads from 12 sources, preprocesses, chunks, and saves to JSON.
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
import tiktoken

# Initialize tiktoken encoder
try:
    encoding = tiktoken.get_encoding("cl100k_base")
except Exception as e:
    print(f"Warning: Could not load tiktoken, using fallback. Error: {e}")
    encoding = None


# ============================================================================
# TOKENIZATION HELPERS
# ============================================================================

def tokenize(text: str) -> List[int]:
    """Tokenize text using tiktoken."""
    if encoding is None:
        # Fallback: simple word tokenization (1 token ≈ 1.3 words)
        return text.split()
    return encoding.encode(text)


def detokenize(tokens: List[int]) -> str:
    """Decode tokens back to text using tiktoken."""
    if encoding is None:
        # Fallback: join words
        return " ".join(tokens)
    return encoding.decode(tokens)


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(tokenize(text))


# ============================================================================
# CHUNKING IMPLEMENTATION
# ============================================================================

def chunk_text(text: str, chunk_size_tokens: int = 350, overlap_tokens: int = 50) -> List[str]:
    """
    Fixed-size chunking with token-based sliding window.
    
    Args:
        text: Text to chunk
        chunk_size_tokens: Target chunk size in tokens (300-400 recommended)
        overlap_tokens: Overlap between chunks in tokens (50 recommended)
    
    Returns:
        List of text chunks
    """
    tokens = tokenize(text)
    chunks = []
    i = 0
    
    while i < len(tokens):
        chunk_end = min(i + chunk_size_tokens, len(tokens))
        chunk_tokens = tokens[i:chunk_end]
        chunk_text_str = detokenize(chunk_tokens)
        chunks.append(chunk_text_str)
        
        # Slide forward: advance by (size - overlap)
        i = chunk_end - overlap_tokens
        
        # If we've reached near the end, break to avoid tiny final chunks
        if chunk_end == len(tokens):
            break
    
    return chunks


# ============================================================================
# PREPROCESSING FUNCTIONS
# ============================================================================

def normalize_dining_hall_names(text: str) -> str:
    """
    Normalize dining hall name variations.
    Maps aliases to canonical names.
    """
    replacements = {
        r'\bFEAST at Rieber\b': 'FEAST',
        r'\bRieber dining\b': 'FEAST',
        r'\bRieber Dining Hall\b': 'FEAST',
        r'\bRieber Hall\b': 'FEAST',
        r'\bDe Neve Dining Hall\b': 'De Neve',
        r'\bDe Neve\b': 'De Neve',
        r'\bBruin Plate\b': 'Bruin Plate',
        r'\bEpicuria\b': 'Epicuria',
        r'\bCafé 1919\b': 'Café 1919',
        r'\bCafe 1919\b': 'Café 1919',
    }
    
    result = text
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def strip_reddit_metadata(text: str) -> str:
    """Remove Reddit-specific metadata: usernames, timestamps, awards, etc."""
    # Remove patterns like "u/username" or "/u/username"
    text = re.sub(r'(?:^|\s)(?:/)?u/\w+', '', text, flags=re.MULTILINE)
    
    # Remove timestamps (e.g., "2 days ago", "3 months ago")
    text = re.sub(r'\b\d+\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago\b', '', text, flags=re.IGNORECASE)
    
    # Remove award patterns (e.g., "Gold", "Silver", "Platinum")
    text = re.sub(r'\b(?:Gold|Silver|Platinum|Helpful|Wholesome|All Seeing Upvote)\b', '', text)
    
    # Remove Reddit formatting artifacts
    text = re.sub(r'\*\*\*', '', text)  # *** formatting
    text = re.sub(r'\n\n+', '\n\n', text)  # Multiple newlines
    
    return text.strip()


def filter_transactional_posts(text: str) -> bool:
    """
    Check if text is primarily transactional (SWIPE trading, for sale, etc.)
    Returns True if should KEEP, False if should FILTER OUT.
    """
    transactional_patterns = [
        r'(?:selling|buying|have|need|looking for)\s+\d+\s+swipes?',
        r'swipes?\s+(?:for\s+sale|for\s+\$)',
        r'\$\d+\s+for\s+\d+\s+swipes?',
        r'(?:anybody|anyone|does?\s+anyone)\s+(?:have|need|want|buy|sell).*swipes?',
    ]
    
    # If post matches transactional patterns, filter out (return False)
    for pattern in transactional_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return False
    
    return True


def preprocess_document(text: str, source: str) -> str:
    """
    Apply full preprocessing pipeline to a document.
    
    Args:
        text: Raw document text
        source: Source URL/name for context-specific processing
    
    Returns:
        Preprocessed text
    """
    # Remove HTML/markup if present
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize dining hall names
    text = normalize_dining_hall_names(text)
    
    # Strip Reddit metadata if from Reddit source
    if 'reddit' in source.lower():
        text = strip_reddit_metadata(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# ============================================================================
# DOCUMENT INGESTION (PLACEHOLDER)
# ============================================================================

def load_sample_documents() -> List[Dict[str, str]]:
    """
    Load sample documents for demonstration.
    In production, this would scrape from 12 sources using APIs/scrapers.
    
    Returns:
        List of dicts with 'text' and 'source' keys
    """
    sample_docs = [
        {
            "text": """FEAST at Rieber is honestly one of the best dining halls. Fresh ingredients, 
            great Asian fusion options. The food quality is consistent. However, wait times during 
            lunch can be brutal—30+ minutes sometimes. The meal plan might be worth it just for FEAST, 
            but De Neve is also solid. Overall, I'd say FEAST edges out other halls.""",
            "source": "https://www.reddit.com/r/ucla/search/?q=dining",
        },
        {
            "text": """De Neve dining hall offers pan-Asian cuisine. The ingredients feel fresher 
            than some other halls. Some inconsistency in quality—one day great, next day mediocre. 
            Good variety for vegetarians. Not the fastest service. Acceptable for a dining hall.""",
            "source": "https://www.google.com/maps/place/De+Neve+Dining+Hall",
        },
        {
            "text": """Is the UCLA meal plan worth it? Mixed opinions. FEAST is great but expensive 
            per swipe. De Neve is better value. Honestly, eating off-campus is often cheaper. 
            If you're on campus a lot, maybe worth it. Otherwise, skip the meal plan.""",
            "source": "https://www.reddit.com/r/ucla/search/?q=meal+plan",
        },
        {
            "text": """Café 1919 is quick for grab-and-go coffee and snacks. Best for speed, not quality. 
            Lines move fast. Good if you're in a rush between classes. Not worth a full meal swipe, 
            but convenient for morning coffee.""",
            "source": "https://www.google.com/maps/place/Café+1919",
        },
        {
            "text": """Epicuria at Ackerman has Mediterranean options. Decent salads and wraps. 
            Less crowded than FEAST or De Neve. Quality is okay, nothing special. Good for a 
            quieter dining experience.""",
            "source": "https://www.google.com/maps/place/Epicuria+at+Ackerman",
        },
        {
            "text": """Bruin Plate is a residential restaurant. More expensive than regular dining halls. 
            Better food quality but you pay extra. Only worth it if you have extra swipes or cash. 
            Not recommended for regular meals.""",
            "source": "https://www.google.com/maps/place/Bruin+Plate+Residential+Restaurant",
        },
        {
            "text": """The dining hall menu system crashed last week and food allergen info was totally wrong. 
            Had a student with peanut allergy nearly eat contaminated food. The allergen tracking is unreliable. 
            They need to fix this ASAP. Very dangerous.""",
            "source": "https://www.reddit.com/r/ucla/search/?q=dining",
        },
        {
            "text": """Rieber dining (FEAST) is closest to my dorm. Convenient location is huge. 
            The food is pretty good, social atmosphere is nice. Other halls require a walk. 
            For Rieber residents, FEAST is ideal.""",
            "source": "https://www.reddit.com/r/uclahousing",
        },
    ]
    
    return sample_docs


# ============================================================================
# CHUNKING WITH METADATA
# ============================================================================

def chunk_documents(documents: List[Dict[str, str]], 
                   chunk_size: int = 350, 
                   overlap: int = 50) -> List[Dict]:
    """
    Chunk documents with metadata tracking.
    
    Args:
        documents: List of dicts with 'text' and 'source'
        chunk_size: Target chunk size in tokens
        overlap: Overlap in tokens
    
    Returns:
        List of chunk dicts with source, chunk_id, text, token_count, original_length
    """
    all_chunks = []
    chunk_id_counter = 0
    
    for doc_idx, doc in enumerate(documents):
        text = doc.get("text", "")
        source = doc.get("source", "unknown")
        
        # Filter out transactional posts
        if not filter_transactional_posts(text):
            print(f"Filtering transactional post from {source}")
            continue
        
        # Preprocess
        text = preprocess_document(text, source)
        
        # Skip very short documents
        if len(text.strip()) < 50:
            continue
        
        original_length = len(text)
        
        # Chunk
        chunks = chunk_text(text, chunk_size_tokens=chunk_size, overlap_tokens=overlap)
        
        for chunk_order, chunk_text_str in enumerate(chunks):
            token_count = count_tokens(chunk_text_str)
            
            chunk_dict = {
                "chunk_id": chunk_id_counter,
                "source": source,
                "chunk_order": chunk_order,
                "text": chunk_text_str,
                "token_count": token_count,
                "original_doc_length": original_length,
                "doc_index": doc_idx,
            }
            all_chunks.append(chunk_dict)
            chunk_id_counter += 1
    
    return all_chunks


# ============================================================================
# SAVE TO JSON
# ============================================================================

def save_chunks_to_json(chunks: List[Dict], output_path: str = "documents/chunks.json"):
    """Save chunks to JSON file with metadata."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        "metadata": {
            "total_chunks": len(chunks),
            "chunk_size_tokens": 350,
            "overlap_tokens": 50,
            "chunking_method": "fixed-size token-based sliding window",
        },
        "chunks": chunks,
    }
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved {len(chunks)} chunks to {output_path}")
    return output_path


# ============================================================================
# VERIFICATION & ANALYSIS
# ============================================================================

def verify_chunks(chunks: List[Dict], sample_size: int = 10):
    """Verify chunk quality: check for splits, overlaps, token counts."""
    import random
    
    if len(chunks) == 0:
        print("No chunks to verify!")
        return
    
    print(f"\n{'='*70}")
    print(f"VERIFICATION REPORT ({sample_size} random samples)")
    print(f"{'='*70}\n")
    
    # Overall stats
    print(f"Total chunks: {len(chunks)}")
    print(f"Average chunk size: {sum(c['token_count'] for c in chunks) / len(chunks):.1f} tokens")
    print(f"Min chunk size: {min(c['token_count'] for c in chunks)} tokens")
    print(f"Max chunk size: {max(c['token_count'] for c in chunks)} tokens")
    
    # Sample inspection
    samples = random.sample(chunks, min(sample_size, len(chunks)))
    
    print(f"\nSample inspections:")
    for i, chunk in enumerate(samples):
        print(f"\n{i+1}. Chunk ID {chunk['chunk_id']} (Source: {chunk['source'][:50]}...)")
        print(f"   Token count: {chunk['token_count']}")
        print(f"   Text preview: {chunk['text'][:100]}...")
        
        # Check if chunk looks split
        if chunk['text'].endswith(('but', 'and', 'or', 'the', 'a', 'an')):
            print(f"   ⚠️  Warning: Chunk ends with incomplete word fragment")
    
    # Check for overlaps (consecutive chunks from same doc)
    overlap_count = 0
    for i in range(len(chunks) - 1):
        if chunks[i]['doc_index'] == chunks[i+1]['doc_index']:
            # Check if there's text overlap
            text1_end = chunks[i]['text'][-50:].lower()
            text2_start = chunks[i+1]['text'][:50].lower()
            if any(word in text2_start for word in text1_end.split()):
                overlap_count += 1
    
    print(f"\nConsecutive chunks with detected overlap: {overlap_count}")
    print(f"Expected overlaps per document: Should see repeated phrases at chunk boundaries")
    
    print(f"\n{'='*70}\n")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_ingestion_pipeline(output_path: str = "documents/chunks.json"):
    """
    Run full ingestion → preprocessing → chunking → save pipeline.
    """
    print("Starting UCLA Dining Ingestion Pipeline...\n")
    
    # Load documents (in production, this calls actual scraper functions)
    print("Loading documents...")
    documents = load_sample_documents()
    print(f"Loaded {len(documents)} documents\n")
    
    # Chunk documents
    print("Chunking documents...")
    chunks = chunk_documents(documents, chunk_size=350, overlap=50)
    print(f"Created {len(chunks)} chunks\n")
    
    # Save to JSON
    print("Saving chunks...")
    output_file = save_chunks_to_json(chunks, output_path)
    print(f"Saved to: {output_file}\n")
    
    # Verification
    print("Running verification...")
    verify_chunks(chunks, sample_size=5)
    
    return output_file, chunks


if __name__ == "__main__":
    output_file, chunks = run_ingestion_pipeline()
    print(f"\nPipeline complete! Chunks saved to: {output_file}")
    print(f"Total chunks generated: {len(chunks)}")
