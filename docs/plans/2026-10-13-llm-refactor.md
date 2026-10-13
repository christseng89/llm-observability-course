# LLM Wrapper Refactor Implementation Plan

**Goal:** Remove duplicate calculations and output without changing API calls or tracing behavior.

**Architecture:** Share cost breakdown, response construction, and terminal formatting. Keep Claude generation recording and the automatic OpenAI integration distinct.

**Tech Stack:** Python, Anthropic, OpenAI, Langfuse.

1. Modify `instrumented_llm.py` to calculate input/output costs once through a shared helper, retaining `calculate_cost` for callers.
2. Extract response construction and output formatting; keep existing public function signatures, model choices, colors, and trace metadata.
3. Validate syntax and run both provider wrappers with fake clients, checking request parameters, usage/cost recording, returned responses, and output without network calls.
