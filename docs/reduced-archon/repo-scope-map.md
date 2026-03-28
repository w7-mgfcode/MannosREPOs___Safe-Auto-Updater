# Reduced Archon — Repo Scope Map (Phase 1.1)

## Scope freeze input
Target slice:
- knowledge base crawling
- document ingestion
- chunking
- embedding generation
- RAG retrieval/search
- MCP exposure for KB/RAG search

Out of scope:
- project/task/document management
- agent work orders
- workflow automation
- UI polish
- non-RAG MCP tools

## Audit summary
This repository appears to be `Safe-Auto-Updater`, not the Archon repository layout referenced in the extraction request.

Expected Archon-style roots (for example `python/src/server/...`, `python/src/mcp_server/...`, `migration/...`) are not present in this repo.

## Scoped inventory (requested paths)

| Requested path | Exists in this repo | Status | Notes |
|---|---:|---|---|
| `python/src/server/api_routes` | No | needs verification | Missing expected Archon server API routes root. |
| `python/src/server/services/crawling` | No | needs verification | Missing expected crawling service root. |
| `python/src/server/services/storage` | No | needs verification | Missing expected storage service root. |
| `python/src/server/services/embeddings` | No | needs verification | Missing expected embeddings service root. |
| `python/src/server/services/search` | No | needs verification | Missing expected search service root. |
| `python/src/server/utils/document_processing.py` | No | needs verification | Missing expected document processing utility. |
| `python/src/mcp_server/features/rag` | No | needs verification | Missing expected MCP RAG feature root. |
| `migration/complete_setup.sql` | No | needs verification | Missing expected SQL setup file. |
| `docker-compose.yml` (repo root) | No | needs verification | Compose file exists under `configs/docker/docker-compose.yml`, not root. |
| Dockerfile for server | Partial | optional | `Dockerfile` exists at repo root, purpose appears updater-focused. |
| Dockerfile for MCP | Partial | needs verification | `deployment/docker/Dockerfile` exists; MCP role unverified. |

## Additional discovered files (potentially adjacent infrastructure)

| Path | Status | Why |
|---|---|---|
| `Dockerfile` | optional | Container build artifact exists; relevance to RAG slice unconfirmed. |
| `deployment/docker/Dockerfile` | needs verification | Secondary Dockerfile exists; service role needs confirmation. |
| `configs/docker/docker-compose.yml` | optional | Compose manifest exists but not in expected Archon root location. |
| `RAG/README.md` | optional | Placeholder folder exists; no implementation scope yet. |

## Keep / optional / remove-later / needs-verification view

### Keep
- _None confirmed yet (blocked by repo mismatch)._ 

### Optional
- `Dockerfile`
- `configs/docker/docker-compose.yml`
- `RAG/README.md`

### Remove later
- _None identified in scope phase; deferring until Archon paths are available._

### Needs verification
- All requested Archon-specific paths listed above
- `deployment/docker/Dockerfile` service ownership and runtime role

## Blocking risk
Without the actual Archon repository (or a branch containing the `python/src/server`, `python/src/mcp_server`, and `migration` trees), Phase 2+ extraction cannot be executed safely.

## Recommended next step
Provide the correct Archon codebase (or point this workspace to the Archon branch/repo), then rerun Phase 1.1 inventory and proceed to boundary mapping.
