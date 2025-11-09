## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SPEC-DRIVEN RAG SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  INPUT LAYER                                                              │
│  ┌────────┐ ┌────────┐ ┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │OpenAPI │ │  gRPC  │ │Terraform│ │  K8s   │ │  Docs  │ │  Docs  │       │
│  │ Specs  │ │ Protos │ │  Files  │ │  YAML  │ │Runbooks│ │  Read  │       │
│  └────────┘ └────────┘ └─────────┘ └────────┘ └────────┘ └────────┘       │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│  INGESTION PIPELINE                                                       │
│  ┌─────────┐      ┌─────────┐      ┌──────────────────┐                   │
│  │ Parse & │  →   │  Clean  │  →   │Extract Metadata  │                   │
│  │Validate │      │Normalize│      │  & Annotations   │                   │
│  └─────────┘      └─────────┘      └──────────────────┘                   │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│  CHUNKING STRATEGY              │  EMBEDDING LAYER                        │
│  • Document → Logical sections  │  Text chunk → Vector [0.23,-0.45,...]   │
│  • OpenAPI example:             │                                         │
│    - Endpoint: /api/users       │  Models: text-embedding-3-large         │
│    - Method: POST + schema      │          nomic-embed / Jina / Voyage    │
│    - Auth: Bearer token         │                                         │
│  • Each chunk = semantic unit   │  Vector DB: Qdrant / Weaviate / Chroma  │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│  RAG PIPELINE                                                             │
│                                                                           │
│  ① QUERY PROCESSING                                                       │
│     User: "What APIs need auth?"                                          │
│     → Query decomposition & expansion                                     │
│     → Generate embedding for query                                        │
│                                    ↓                                      │
│  ② HYBRID RETRIEVAL                                                       │
│     • Vector Search (semantic similarity)                                  │
│     • Keyword Search (metadata: auth_required=true)                        │
│     → Retrieve top-k candidates (k=20-50)                                  │
│                                    ↓                                       │
│  ③ RE-RANKING                                                             │   
│     • Cross-encoder scoring                                                │
│     • Filter by relevance threshold                                        │
│     → Select top-n chunks (n=5-10)                                         │
│                                    ↓                                       │
│  ④ CONTEXT ASSEMBLY                                                       │
│     • Format specs with metadata                                           │
│     • Add source attribution                                               │
│     • Token budget management                                              │
│                                    ↓                                       │
│  ⑤ LLM GENERATION                                                         │
│     System: "You are ops assistant. Use ONLY specs. Never hallucinate"    │
│     Context: [Retrieved spec chunks with sources]                         │
│     Query: "What APIs need auth?"                                         │
│     → Generate grounded response                                          │
│                                    ↓                                      │
│  ⑥ GUARDRAILS & VALIDATION                                                │
│     • Verify citations present                                            │
│     • Check for hallucination patterns                                    │
│     • PII filtering                                                       │
└───────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────────────────────────────────────────────────────────────────┐
│  OBSERVABILITY LAYER                                                      │
│  • Latency metrics (retrieval, generation, e2e)                           │
│  • Retrieval quality (precision@k, recall@k)                              │
│  • Token usage tracking                                                   │
│  • User feedback loop                                                     │
└───────────────────────────────────────────────────────────────────────────┘
```