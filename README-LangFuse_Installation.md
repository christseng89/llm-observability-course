# LLM Evaluation & Observability

> Measure Quality. Understand Behavior. Deliver Value.

## LLM Evaluation

> Evaluate whether an LLM application produces high-quality results.

- **AI Apps** (AI Engineers)
- LLM Models (3rd Parties, out of scope)

### Key Activities

- Build golden datasets
- Run LLM tests
- Apply evaluation metrics
- Analyze results
- Improve application quality

### Evaluation Dimensions

- Correctness
- Relevance
- Faithfulness
- Completeness
- Safety and reliability

## LLM Observability

Understand how the application behaves in real usage.

### What to Observe

- LLM calls
- Retrieval steps
- Tool calls
- Agent workflows
- Latency and costs
- Production failures

## Combined Workflow

Build → Evaluate → Trace → Monitor → Improve

---
# LangFuse Docker Compose Installation

- <https://langfuse.com/self-hosting/deployment/docker-compose>

```bash
# Clone Langfuse Repository
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Start the application
docker compose up -d

```
## Browser

<http://localhost:3000>

---

> Install the Langfuse AI skill from github.com/langfuse/skills and use it to add tracing to this application with Langfuse following best practices.
