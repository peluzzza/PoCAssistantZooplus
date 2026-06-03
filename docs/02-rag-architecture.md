# RAG architecture

**Status:** PENDING — complete in **T2**  
**Proposal reference:** [`plans/PROPOSAL.md`](plans/PROPOSAL.md) §8, §16

---

## Design anchors (from proposal)

- **Filter-then-score:** `site_id` hard filter before vector ranking  
- **Raw JSON immutable:** `data/raw/` or `instructions/` copy  
- **Artifacts:** `artifacts/index/` (Chroma PoC)  
- **Chunk unit:** one embedding document per variant (confirm in T2)  

**Evidence:** `trace/T2-rag-index.md`
