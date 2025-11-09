**Scenario 1: Auth Requirements Query**

```
User: "Which APIs require authentication?"

Expected RAG Response:
"Based on the specifications:

1. User Management API (/api/users):
   - Requires: Bearer JWT token
   - Source: user_service.yaml → securitySchemes.bearerAuth

2. Payment API (/api/payments):
   - Requires: API Key + OAuth 2.0
   - Source: payment_api.json → security section

3. User Service Deployment:
   - ENV: AUTH_REQUIRED=true
   - JWT_SECRET from k8s secret
   - Source: deployment.yaml → spec.containers.env
```
**Scenario 2: GitLab MCP Integration**[^2_9][^2_8]

```
User: "Show me failed CI/CD pipelines and their logs"

MCP Action:
1. GitLab MCP calls get_merge_request_pipelines_service
2. Filters for status: "failed"
3. Retrieves pipeline_jobs logs
4. Returns formatted results with links
```

**Scenario 3: Cross-Spec Analysis**

```
User: "Compare auth implementations across OpenAPI, K8s, and Terraform"

RAG Pipeline:
1. Vector search: "authentication security"
2. Metadata filter: file_type in [openapi, k8s, terraform]
3. Rerank by relevance
4. Context assembly with all three sources
5. LLM generates comparison table
```