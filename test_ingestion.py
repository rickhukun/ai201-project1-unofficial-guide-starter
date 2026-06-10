"""
Quick test script for ingestion and chunking pipeline.
Run this to verify the pipeline works end-to-end.
"""

from ingestion import run_ingestion_pipeline, verify_chunks, load_sample_documents, chunk_documents
import json


def test_tokenization():
    """Test tokenization and detokenization."""
    from ingestion import tokenize, detokenize, count_tokens
    
    print("=" * 70)
    print("TEST: Tokenization")
    print("=" * 70)
    
    test_text = "FEAST at Rieber is one of the best dining halls. Fresh ingredients, great quality."
    
    tokens = tokenize(test_text)
    recovered_text = detokenize(tokens)
    token_count = count_tokens(test_text)
    
    print(f"Original text: {test_text}")
    print(f"Token count: {token_count}")
    print(f"Recovered text: {recovered_text}")
    print(f"✓ Tokenization test passed\n")


def test_chunking():
    """Test fixed-size chunking with overlap."""
    from ingestion import chunk_text, count_tokens
    
    print("=" * 70)
    print("TEST: Fixed-size Chunking (350 tokens, 50-token overlap)")
    print("=" * 70)
    
    long_text = """
    FEAST at Rieber is honestly one of the best dining halls on campus. 
    The food quality is consistently fresh, and they offer great Asian fusion options 
    that you won't find at other halls. De Neve has some good variety, but FEAST 
    edges them out. The only downside is wait times during lunch can be brutal—30+ 
    minutes sometimes. The meal plan might be worth it just for FEAST access. 
    Overall, I'd rate FEAST 8/10 for quality and convenience.
    
    De Neve dining hall offers pan-Asian cuisine which is great for dietary variety. 
    The ingredients feel fresher than some other halls, but there's occasional 
    inconsistency—one day great, next day mediocre. The service isn't the fastest, 
    but acceptable for a dining hall. Good options for vegetarians. I'd rate De Neve 7/10.
    
    Café 1919 is my go-to for quick coffee and snacks between classes. 
    Best for speed, not quality. Lines move fast, which is the main advantage. 
    It's good if you're in a rush but not worth a full meal swipe.
    """
    
    chunks = chunk_text(long_text, chunk_size_tokens=350, overlap_tokens=50)
    
    print(f"Total chunks created: {len(chunks)}")
    print(f"Long text token count: {count_tokens(long_text)}\n")
    
    for i, chunk in enumerate(chunks):
        token_count = count_tokens(chunk)
        print(f"Chunk {i + 1}: {token_count} tokens")
        print(f"  Preview: {chunk[:80]}...")
        print()
    
    print("✓ Chunking test passed\n")


def test_preprocessing():
    """Test preprocessing functions."""
    from ingestion import normalize_dining_hall_names, strip_reddit_metadata, filter_transactional_posts
    
    print("=" * 70)
    print("TEST: Preprocessing Functions")
    print("=" * 70)
    
    # Test 1: Dining hall name normalization
    test_text = "I love FEAST at Rieber and Rieber dining is great. De Neve is also cool."
    normalized = normalize_dining_hall_names(test_text)
    print("1. Dining Hall Normalization:")
    print(f"   Before: {test_text}")
    print(f"   After:  {normalized}\n")
    
    # Test 2: Reddit metadata stripping
    test_reddit = "u/username posted 2 days ago: The food is great! Gold Award"
    stripped = strip_reddit_metadata(test_reddit)
    print("2. Reddit Metadata Stripping:")
    print(f"   Before: {test_reddit}")
    print(f"   After:  {stripped}\n")
    
    # Test 3: Transactional post filtering
    transactional = "Selling 20 swipes for $10. Anyone interested? DM me."
    genuine_review = "FEAST food quality is amazing, highly recommend."
    
    print("3. Transactional Post Filtering:")
    print(f"   Transactional post filtered? {not filter_transactional_posts(transactional)}")
    print(f"   Genuine review kept? {filter_transactional_posts(genuine_review)}\n")
    
    print("✓ Preprocessing test passed\n")


def test_full_pipeline():
    """Test the complete ingestion pipeline."""
    print("=" * 70)
    print("TEST: Full Ingestion Pipeline")
    print("=" * 70 + "\n")
    
    output_file, chunks = run_ingestion_pipeline(
        output_path="documents/chunks_test.json"
    )
    
    print(f"\n✓ Full pipeline test passed")
    print(f"  Output file: {output_file}")
    print(f"  Total chunks: {len(chunks)}")


def test_chunk_quality():
    """Verify chunk quality metrics."""
    from ingestion import count_tokens
    
    print("=" * 70)
    print("TEST: Chunk Quality Metrics")
    print("=" * 70 + "\n")
    
    documents = load_sample_documents()
    chunks = chunk_documents(documents, chunk_size=350, overlap=50)
    
    # Calculate statistics
    token_counts = [c['token_count'] for c in chunks]
    avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
    min_tokens = min(token_counts) if token_counts else 0
    max_tokens = max(token_counts) if token_counts else 0
    
    # Count chunks in expected range
    in_range = sum(1 for c in token_counts if 300 <= c <= 400)
    
    print(f"Chunk Statistics:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Average size: {avg_tokens:.1f} tokens")
    print(f"  Min size: {min_tokens} tokens")
    print(f"  Max size: {max_tokens} tokens")
    print(f"  Chunks in 300-400 range: {in_range}/{len(chunks)} ({100*in_range/len(chunks):.1f}%)")
    print()
    
    # Expected: Most chunks should be 300-400 tokens
    expected_percent = 80  # At least 80% in range
    if 100 * in_range / len(chunks) >= expected_percent:
        print(f"✓ Quality test passed ({in_range}/{len(chunks)} chunks in target range)\n")
    else:
        print(f"⚠️  Quality warning: Only {100*in_range/len(chunks):.1f}% in target range\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("UCLA DINING INGESTION & CHUNKING PIPELINE - TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_tokenization()
        test_chunking()
        test_preprocessing()
        test_chunk_quality()
        test_full_pipeline()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Review chunks.json in documents/ folder")
        print("2. Manually inspect 5-10 chunks for quality")
        print("3. Verify overlap between consecutive chunks")
        print("4. Check that no single review is split across 3+ chunks")
        print("5. Move to Milestone 4: Embedding & Retrieval\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
