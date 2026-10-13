# Instrumented LangFuse via LLM or LangChain

## Hands on Instrumented via LLM

```bash
uv run instrumented_llm.py
```

## Instrumenting Multi-Step Pipelines（多步驟流程的可觀測性追蹤）

> RAG + Agent Patterns（RAG 與 AI Agent 設計模式）

| # | Key Practice                              | 中文說明                                                           |
| - | ----------------------------------------- | -------------------------------------------------------------- |
| 1 | Each Step Becomes a Span in the Trace     | 將每個處理步驟記錄為 Trace 中的 Span，方便追蹤各階段的執行時間與結果。                      |
| 2 | Capture Metadata at Every Stage           | 在每個處理階段記錄 Metadata，例如執行狀態、模型、參數及處理結果。                          |
| 3 | Track Retrieval Quality (Distance Scores) | 追蹤 RAG 檢索品質，例如 Vector Similarity / Distance Scores，評估文件片段的相關性。 |
| 4 | Measure Context Size (Token Implications) | 測量傳送給 LLM 的 Context Size，分析其對 Token Usage、API Cost 及效能的影響。     |

核心概念： 在 Langfuse 中，應將 RAG / AI Agent 的各個處理階段分別追蹤，其中一般處理步驟使用 **Span**，LLM API Calls 使用 **Generation**，以便分析完整 Pipeline 的效能、成本及品質。

---

## Hands on RAG

```bash
uv run rag_pipeline_obs.py
```

> Reads Markdown files from ./docs, splits them into chunks, generates embeddings, and stores the chunks, embeddings, and source metadata in ChromaDB, persisted at ./chroma_db.

### Tracers
- rag_load_and_index_docs
- rag_pipeline

---

## Hands on Instrumented via LangChain

```bash
uv run instrumented_langchain.py
```
