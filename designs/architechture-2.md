### Demo Stack Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    LIVE DEMO: SPEC-DRIVEN RAG + MCP                  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  PLATFORM: Open WebUI (Self-hosted RAG Platform)                    │
│  URL: http://localhost:3000                                          │
│  Features: Built-in RAG, Hybrid Search, Custom Pipelines            │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  LLM BACKEND (Choose one - All FREE)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Ollama Local │  │ Groq Cloud   │  │GitHub Models │               │
│  │ (Llama 3.1)  │  │ (Free API)   │  │ (Free tier)  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  MCP SERVERS (Context Providers)                                     │
│                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │ GitLab MCP Server    │  │ Kubernetes MCP       │                 │
│  │ • Projects/Issues    │  │ • Pod status         │                 │
│  │ • Pipelines/MRs      │  │ • Deployments        │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
│                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │ Fetch MCP Server     │  │ Sequential Thinking  │                 │
│  │ • Web scraping       │  │ • Problem solving    │                 │
│  │ • HTML→Markdown      │  │ • Reasoning chains   │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  VECTOR DATABASE: Qdrant (Local Docker)                             │
│  Embedding Model: nomic-embed-text (via Ollama)                     │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  SAMPLE SPEC DOCUMENTS (Your Input Layer)                           │
│  • OpenAPI specs (Swagger JSONs)                                     │
│  • Kubernetes YAML manifests                                         │
│  • Terraform .tf files                                               │
│  • GitLab CI/CD pipelines                                            │
│  • Monitoring configs (Prometheus)                                   │
└──────────────────────────────────────────────────────────────────────┘
```