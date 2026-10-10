# Setup

```bash
git clone https://github.com/christseng89/llm-observability-course.git LangFuse
cd LangFuse

pyenv global 3.12.10
pyenv local 3.12.10

uv sync
```
---

# ROI Framework

Real cost comparison with Observability

| Category          | Without Obs. | With Obs. |
| ----------------- | ------------ | --------- |
| Monthly LLM spend | $35,000+     | $15,000   |
| Wasted retries    | $5,000+      | \~$0      |
| Debug time/week   | 20+ hours    | 2 hours   |
| Incident response | Days         | Same day  |

---

# Real Cost Breakdown

| Category     | Cost Components       |
| ------------ | --------------------- |
| 🔴 API Costs | Tokens                |
| 🟠 Compute   | Embeddings, Inference |
| 🟡 Debugging | Engineering Hours     |
| 🟢 Incidents | Downtime, Reputation  |

---

# The Cost Spiral

Token costs increased by 400%^

| Month | Cost |
| ----- | ---- |
| M1    | 1    |
| M2    | 1.75 |
| M3    | 2.6  |
| M4    | 5    |

M1–M4 values are illustrative; the source image does not provide exact monthly amounts.

> "Token costs grew 400% — we only found out at month end"

— Real quote from enterprise teams

Key takeaway: Without proper LLM observability, token consumption and API costs can increase significantly before teams detect the issue.

---
# Risk Matrix

Without observability

| Risk                    | Impact          | Probability  |
| ----------------------- | --------------- | ------------ |
| Token spike             | 🔴 High ($10K+) | 🔴 **Very High** |
| Silent failures         | 🟠 Medium       | 🔴 High      |
| Performance degradation | 🟠 Medium       | 🔴 High      |
| Compliance violation    | 🔴 **Critical**     | 🟠 Medium    |

## Without observability 四項風險

| Risk                       | 真實業務情境                              | 主要影響        | 建議監控                             |
| -------------------------- | ----------------------------------- | ----------- | -------------------------------- |
| 🔴 Token Spike             | AI Agent 重複呼叫 LLM，Token 暴增          | API 成本失控    | Token Usage、Cost、Retries         |
| 🟠 Silent Failures         | AI 遺漏 LC 文件不符點，但 API 回傳成功           | 業務損失、錯誤決策   | Output Validation、Business Rules |
| 🟡 Performance Degradation | Payment Investigation 從 5 秒增加至 30 秒 | 交易延遲、服務品質下降 | P95 Latency、Tool Duration        |
| 🔴 Compliance Violation    | 客戶敏感資料被記錄到未授權平台                     | 法規、財務、聲譽風險  | PII Detection、DLP、Audit Logs     |

---

# Traditional vs LLM Observability

# LLM Observability Areas

| LLM Observability Area | Description                                                     | Key Questions                                   |
| ---------------------- | --------------------------------------------------------------- | ----------------------------------------------- |
| Token Flows            | Monitor token usage and consumption across LLM requests         | How many input/output tokens? What's the ratio? |
| Model Behavior         | Track model responses, accuracy, and behavior                   | Is the LLM hallucinating（幻覺）?                   |
| Prompt Effectiveness   | Evaluate prompt quality and effectiveness                       | Is the prompt producing good results?           |
| Cost Attribution       | Track and attribute LLM costs to models, applications, or users | Which feature is consuming your budget?         |
| Retrieval Quality      | Evaluate the relevance and accuracy of retrieved information    | Is your RAG returning relevant chunks?          |

---

# Traditional vs LLM Observability

| Traditional Monitoring     | LLM Observability     |
| -------------------------- | --------------------- |
| Request → [???] → Response | Full trace visibility |
| Black box view             | Token flows tracked   |
| Only latency & errors      | Prompt effectiveness  |
| —                          | Cost attribution      |

---
# The Three Pillars for LLMs

| #    | Pillar      | Description                                 |
| ---- | ----------- | ------------------------------------------- |
| 🔴 1 | Traces      | End-to-end request flows through every step |
| 🟢 2 | Metrics     | Token usage, latency, costs per request     |
| 🔵 3 | Evaluations | Quality scores and output assessment        |

---

# What You'll Measure

- Token usage (input/output ratio)
- Latency (per step breakdown)
- Cost (per request, per feature, per user)
- Quality (relevance, hallucination rate)
- Errors (by type, by model, by prompt)

---

# ROI Calculator

## Current State (Without Observability)

| Category                     | Monthly Cost |
| ---------------------------- | ------------ |
| Monthly LLM spend            | $20,000      |
| Estimated waste (30%)        | $6,000       |
| Debug time (10 hr/wk × $100) | $4,000/mo    |
| Incident cost (amortized)    | $5,000/mo    |
| Total Preventable Cost       | $15,000/mo   |

### Investment

- Platform: $500–$2,000/month
- Setup: 8 hours one-time

## ROI (with Observability)

Estimated ROI => 7–30 times return in the first month alone

| 情境    | 每月節省    | 平台費用   | Return Multiple |
| ----- | ------- | ------ | --------------- |
| 高成本方案 | $15,000 | $2,000 | 7.5×            |
| 低成本方案 | $15,000 | $500   | 30×             |

### 正確計入第一個月的 Setup Cost

假設導入工程師成本沿用簡報的每小時 $100：

Setup Cost = 8 × $100 = $800。

| 項目                     | 低成本方案   | 高成本方案   |
| ---------------------- | ------- | ------- |
| Monthly Savings        | $15,000 | $15,000 |
| Platform Cost          | $500    | $2,000  |
| Setup Cost             | $800    | $800    |
| First Month Investment | $1,300  | $2,800  |
| Net Savings            | $13,700 | $12,200 |
| Benefit / Cost         | 11.54×  | 5.36×   |
| Net ROI                | 1,054%  | 436%    |

### Consecutive Monthly ROI (Month 2 Onward)

| Item                  | Low-Cost Plan | High-Cost Plan |
| --------------------- | ------------- | -------------- |
| Monthly Savings       | $15,000       | $15,000        |
| Monthly Platform Cost | $500          | $2,000         |
| Setup Cost            | $0            | $0             |
| Monthly Net Savings   | $14,500       | $13,000        |
| Benefit / Cost        | 30×           | 7.5×           |
| Monthly Net ROI       | 2,900%        | 650%           |

> Net ROI = Net Savings / First Month Investment * 100%

### Real Results

| Improvement            | Result | Description                 |
| ---------------------- | ------ | --------------------------- |
| Token cost reduction   | 47%    | From prompt optimization    |
| Less debug time        | 80%    | With proper tracing         |
| Runaway cost surprises | $0     | No unexpected runaway costs |

---
