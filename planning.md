# Project 1 Planning: The Unofficial Guide

---

## Domain

Student experiences and opinions about UCLA dining halls — what the food is really like, meal plan value, wait times, dietary accommodations, and which halls are worth the meal plan cost. This knowledge is scattered across Reddit threads, Yelp reviews, and word-of-mouth, but UCLA's official dining website only shows menus and hours, not honest student perspectives.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/UCLA Dining Discussions | Reddit thread about meal plan value and dining hall experiences | https://www.reddit.com/r/ucla/search/?q=dining |
| 2 | r/UCLA Meal Plan Thread | Student opinions on meal plan worth and SWIPE usage | https://www.reddit.com/r/ucla/search/?q=meal+plan |
| 3 | FEAST at Rieber (Google Reviews) | Dining hall reviews with ratings | https://www.google.com/maps/place/FEAST+at+Rieber |
| 4 | De Neve (Google Reviews) | Pan-Asian cafeteria reviews | https://www.google.com/maps/place/De+Neve+Dining+Hall |
| 5 | Bruin Plate (Google Reviews) | Residential restaurant reviews and ratings | https://www.google.com/maps/place/Bruin+Plate+Residential+Restaurant |
| 6 | Epicuria at Ackerman (Google Reviews) | Mediterranean dining hall reviews | https://www.google.com/maps/place/Epicuria+at+Ackerman |
| 7 | Café 1919 (Google Reviews) | Coffee and grab-and-go option reviews | https://www.google.com/maps/place/Café+1919 |
| 8 | r/college UCLA Dining Thread | Broader college subreddit with UCLA dining discussions | https://www.reddit.com/r/college/search/?q=UCLA+dining |
| 9 | r/UCLA Housing Posts | Housing discussions that mention dining experiences | https://www.reddit.com/r/uclahousing |
| 10 | YouTube UCLA Dining Reviews | Video reviews of UCLA dining halls and meal plan | https://www.youtube.com/search?q=UCLA+dining+hall+review |
| 11 | BruinWalk UCLA Housing Guide | Student-created guides mentioning dining | https://bruinwalk.com |
| 12 | UCLA Official Dining Website | Menus, hours, and dining plan info | https://www.dining.ucla.edu |

---

## Chunking Strategy

**Chunk size:** 300–400 tokens (roughly 200–250 words)

**Overlap:** 50 tokens (≈ 2–3 sentences, 12–15% of chunk size)

**Method:** Fixed-size chunking with token-based sliding window

**Rationale:** Mixed-length corpus (short Reddit + long discussions) benefits from fixed-size consistency. 50-token overlap bridges topic transitions; most reviews stay intact (~5% fragmentation acceptable for simplicity).

**Implementation:**
```python
def chunk_text(text, chunk_size_tokens=350, overlap_tokens=50):
    """
    Fixed-size chunking with token-based sliding window.
    """
    tokens = tokenize(text)  # Use tiktoken
    chunks = []
    i = 0
    
    while i < len(tokens):
        chunk_end = min(i + chunk_size_tokens, len(tokens))
        chunks.append(detokenize(tokens[i:chunk_end]))
        i = chunk_end - overlap_tokens  # Slide forward by (size - overlap)
    
    return chunks
```

**Expected result:** ~300–500 chunks from 100 dining sources, with most chunks between 300–400 tokens and robust topic coherence due to 50-token overlap.

---

## Retrieval Approach

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` (Hugging Face, 22M parameters)

**Top-k:** 6 chunks per query

**Model choice rationale:** 
All-MiniLM-L6-v2 is ideal for your domain because:
- Lightweight (22M params, <5MB) — fast inference, easy to deploy
- Trained on general-domain sentence-level semantics, handles short opinion text well
- Designed for short text (reviews, tweets) rather than long documents
- Good semantic understanding of subjective language ("great," "overpriced," "crowded")
- Sufficient accuracy on opinion-based text (tradeoff: less nuanced than larger models, but acceptable)

**Why top-k=6 is right for dining opinions:**

| k Value | Problem | Why k=6 Works Better |
|---------|---------|----------------------|
| k=1–2 | One outlier opinion dominates. Query "Is FEAST worth it?" gets one negative review, LLM can't surface the mixed consensus. | Multiple perspectives (3–5 chunks typically) on same hall rank high due to semantic similarity. Diverse opinions = LLM can say "Mixed: some say X, others say Y" |
| k=6 ✅ | Balanced. Captures 3–5 perspectives on same topic, avoiding outliers while maintaining diversity. | For opinions, higher k needed than facts. One person's "terrible food" vs. another's "great value" both valid—need both to ground answer. |
| k=20+ | Information overload. Conflicting opinions blur together. Off-topic chunks appear (e.g., "Rieber dorm layout" when querying dining quality). LLM drowns in noise. | Diminishing returns: extra chunks rarely add new insight; mainly repeat existing opinions or introduce noise. |

**Why it works:** Embeddings capture semantic meaning. "Fresh" ≈ "new" ≈ "crisp" in vector space, so queries match synonyms without exact words.

**Production tradeoff:** Larger models (all-mpnet, 420M params) offer 10–15% better nuance; multilingual models handle international students; hybrid search (semantic + keyword) helps with dining hall name aliasing. MiniLM chosen for speed + simplicity.

---

## Guiding Insights for Implementation

**Question: How many chunks is enough?**
- **Too few (k=1–2):** One person's opinion dominates. System lacks confidence; can't surface consensus or disagreement.
- **Too many (k=20+):** Noise balloons. Conflicting opinions drown each other out. LLM struggles to summarize.
- **k=6 sweet spot:** Enough perspectives for confidence, few enough to avoid noise. For dining reviews, typically retrieves 3–5 different perspectives on same topic.

**Question: Why semantic search works without exact word matches?**
Embeddings learned from pre-training capture synonym relationships. "Fresh" and "new" have similar vector representations. So queries about "freshness" match chunks about "newness" even with zero word overlap. This is why semantic search beats keyword matching for opinion-based text.

**Question: Top-k tradeoffs in a nutshell?**
- Low k → confident but risky (one outlier ruins answer)
- High k → safe but noisy (conflicting info overwhelms LLM)
- For opinions (dining reviews), use higher k than for facts (technical docs)

---

## Evaluation Plan

| # | Question | Verification Criteria (Objective) |
|---|----------|----------------------------------|
| 1 | What do students say about food quality at De Neve dining hall? | System retrieves ≥2 chunks from different sources (Reddit + Google Reviews) mentioning De Neve. Answer includes ≥2 of: {fresh/quality ingredients, Asian cuisine, inconsistency, wait times}. **Verifiable:** Can spot-check retrieved chunks for dining hall name + quality adjectives. |
| 2 | Is the UCLA meal plan worth the cost according to students? | System surfaces ≥2 contrasting opinions: (a) at least one chunk saying meal plan is good value/worth cost, (b) at least one saying it's overpriced/expensive. **Verifiable:** Can search retrieved chunks for keywords like "worth," "overpriced," "expensive," "good value" and confirm opinion polarity. |
| 3 | Which dining halls have the shortest wait times during peak lunch hours? | System retrieves ≥3 chunks discussing wait times. Answer names ≥2 specific halls with comparative speed (e.g., "Café 1919 is quick" vs. "FEAST is busy"). **Verifiable:** Can check if hall names are explicitly mentioned + wait time descriptions are comparative/quantified. |
| 4 | Do UCLA dining halls accommodate dietary restrictions like vegetarian or allergy-free meals? | System retrieves ≥2 chunks discussing dietary accommodations. Answer identifies ≥1 specific accommodation gap (allergen tracking failures, limited vegetarian options, menu system errors). **Verifiable:** Can check for concrete problem descriptions or references to specific meal restrictions. |
| 5 | Are FEAST dining options good for students with limited budgets (e.g., minimal meal plan swipes)? | System retrieves ≥2 chunks discussing meal plan cost/value for FEAST specifically. Answer references ≥1 of: {swiped meal portion size, pricing per item, value vs. off-campus alternatives}. **Verifiable:** Can confirm chunks contain FEAST + cost/value language ("worth," "portion," "swiped," "$"). |

---

## Anticipated Challenges

1. **Format inconsistency + caveat loss:** Short Reddit (1 sent) + long narratives (6+ para) + Google Reviews (1–2 sent) noise. "De Neve is great, but..." may lose caveats. **Fix:** 50-token overlap + preprocessing.

2. **Complaint bias:** Negative posts >> positive posts. System may overstate dining problems. **Fix:** Track sentiment; evaluate source diversity.

3. **Dining hall aliasing:** "FEAST," "FEAST at Rieber," "Rieber dining" not linked by embeddings. **Fix:** Normalization layer before chunking.

4. **Off-topic noise:** SWIPE trading posts ("20 swipes left") embedded as dining content. **Fix:** Filter transactional posts; tag chunks by topic.

---

## AI Tool Plan

**Milestone 3 — Document ingestion & chunking:**
- Input: planning.md (domain, sources, chunking strategy, challenges) + 12 source URLs
- Task: Scrape/download → normalize dining hall names → filter off-topic posts → apply 300–400 token chunking with 50-token overlap → save JSON (source, chunk_id, original_length)
- Output: ~300–500 chunks in JSON format
- Verify: 10 random chunks; confirm no review split 3+ ways; overlap repeats 2–3 sentences

**Milestone 4 — Embedding & retrieval:**
- Input: Chunked JSON + retrieval approach section
- Task: Embed with all-MiniLM-L6-v2 → store in FAISS → build top-k=6 retrieval function
- Output: Retrieval function for test queries
- Verify: 5 evaluation questions; chunks should be relevant to query (e.g., "De Neve?" → De Neve chunks, not random halls)

**Milestone 5 — Grounded generation:**
- Input: Retrieval function + evaluation questions + anticipated challenges
- Task: System prompt enforcing (1) answer only from chunks, (2) cite sources, (3) surface disagreements → LLM wrapper for test questions
- Output: Grounded answers for 5 evaluation questions
- Verify: Answers cite sources; no hallucinations; matches expected answers from evaluation plan
