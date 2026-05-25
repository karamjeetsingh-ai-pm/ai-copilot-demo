# Astra AI — Copilot & Insights

This repo is the architectural demonstration of that system — adapted for a B2B revenue and marketing intelligence context, with three modes of interaction designed to show different layers of what production AI looks like.



## The Problem It Solves

The ask: let CMOs query the platform in natural language, the way they'd ask a trusted analyst — and get an answer in 20 minutes, not 3 days.

---

## Three Modes

### Mode 1 · Copilot Chat
Natural language querying over brand and revenue data.

```
"How is Maggi doing vs. last quarter on e-commerce?"
"Which category is underperforming on Meta vs. Google?"
"Where should I reallocate budget this month?"
```

The copilot retrieves from the right data source, synthesises an answer with narrative context, attaches citations, and flags confidence level. Not a data table — an answer a CMO would accept in a board meeting.

**Architecture:**
```
User Query
    │
Query Router (intent + entity extraction)
    │
    ├── Brand Scores DB (Supabase vector store)
    ├── Social/Ecom Signals (Tavily real-time)
    └── Media Attribution Data
    │
Prompt Compression (−35% token cost)
    │
LLM Generation (Gemini 1.5 Flash)
    │
Hallucination Check (answer vs. retrieved chunks)
    │
Response + Citations + Confidence Score
```

**Key PM decisions:**
- **Narrative over tables** — CMOs want analysis, not raw data. The system prompt instructs the model to answer as a trusted analyst, not a database
- **Confidence indicator** — every response shows a confidence level. Users learn to calibrate trust; they're not surprised when the system is uncertain
- **Multi-source retrieval** — not single-source RAG. The query router identifies which data sources the question requires and retrieves from each in parallel
- **Prompt compression** — summarise retrieved chunks before passing to the LLM. Reduces token count 35%, cuts inference cost 28%, no material accuracy loss

---

### Mode 2 · Agent Executor
Tool-calling AI agents that can take actions, not just answer questions.

The Agent Executor demonstrates the **ReAct pattern** (Reason + Act) — the agent reasons about what it needs to do, calls the right tools, observes the result, and iterates until it has an answer.

```
Complex Query
    │
Agent Reasoning (what do I need to find out?)
    │
Tool Selection + Execution
    │    ├── search_brand_data()
    │    ├── compare_time_periods()
    │    ├── fetch_competitor_signals()
    │    └── calculate_budget_impact()
    │
Observation (what did the tool return?)
    │
Next Action (do I have enough? or search more?)
    │
Final Answer (synthesised from tool outputs)
```

**Why this matters for enterprise AI:** Single-shot RAG answers one question. Agents handle multi-step queries that require sequencing — "compare Q3 vs Q4, identify the biggest drop, and suggest the three likeliest causes." That requires chaining tool calls, not one retrieval.

---

### Mode 3 · Decision Board
Human-in-the-Loop (HITL) interface for AI-generated recommendations.

The Decision Board is where AI-generated recommendations surface for human review, modification, and approval. It's the governance layer that makes the system safe to use at enterprise scale.

```
AI Recommendation Queue
    │
Decision Card Display
    ├── Recommendation (what AI suggests)
    ├── Reasoning (why AI suggests it)
    ├── Confidence (how certain is the AI)
    ├── Supporting Data (what evidence)
    └── Risk Flag (if applicable)
    │
Human Action
    ├── ✅ Approve → executed
    ├── ✏️  Modify → human edits, then executes
    └── ❌ Reject → logged with reason (feeds back to model)
```

**Why HITL is a product feature, not a safety net:** The rejection signal is fed back as evaluation data. Over time, patterns in what gets rejected tell you exactly where the model is calibrated wrong — better than any automated eval.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                 Astra AI Copilot                     │
│                                                     │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ Copilot Chat│ │Agent Executor│ │Decision Board│ │
│  └──────┬──────┘ └──────┬───────┘ └──────┬───────┘ │
│         │               │                │         │
│         └───────────────┼────────────────┘         │
│                         │                          │
│              ┌──────────▼──────────┐               │
│              │   LangChain ReAct   │               │
│              │   Orchestration     │               │
│              └──────────┬──────────┘               │
│                         │                          │
│         ┌───────────────┼───────────────┐          │
│         │               │               │          │
│  ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐  │
│  │  Supabase   │ │   Tavily    │ │  Gemini /  │  │
│  │ Vector Store│ │ Real-time   │ │   Groq     │  │
│  │  (RAG)      │ │  Search     │ │   (LLM)    │  │
│  └─────────────┘ └─────────────┘ └────────────┘  │
└─────────────────────────────────────────────────────┘
```

---


## What Makes This Different from a Chatbot Demo

| Typical AI Demo | Astra AI Copilot |
|----------------|-----------------|
| Single LLM call | Multi-source retrieval + synthesis |
| No eval framework | RAGAS scoring + human-eval pipeline |
| No observability | Langfuse tracing on every request |
| Static data | Real-time + vector store hybrid |
| One interaction mode | Chat + Agent + HITL in one platform |
| No cost control | Prompt compression layer (−28% cost) |
| Black box | Every answer has citations + confidence |

---

## Repo Structure

```
ai-copilot-demo/
├── app/
│   ├── ui/
│   │   ├── chat_view.py        # Copilot Chat — RAG query interface
│   │   ├── agent_view.py       # Agent Executor — ReAct tool-calling
│   │   └── decision_view.py    # Decision Board — HITL review interface
│   ├── rag/
│   │   ├── retriever.py        # Multi-source retrieval pipeline
│   │   └── embeddings.py       # Vector store management
│   └── agents/
│       └── react_agent.py      # LangChain ReAct agent + tools
├── config.py                   # Model config + API setup
├── streamlit_app.py            # Entry point + session + routing
└── requirements.txt
```

---

## Quick Start

```bash
git clone https://github.com/karamjeetsingh-ai-pm/ai-copilot-demo
cd ai-copilot-demo
pip install -r requirements.txt

# Add API keys to .env
# GEMINI_API_KEY, GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, TAVILY_API_KEY

streamlit run streamlit_app.py
```

---


## Built by

**Karamjeet Singh** · Lead AI Product Manager · [karamjeetsingh.com](https://www.karamjeetsingh.com)

[LinkedIn](https://www.linkedin.com/in/karamjeetsingh-ai-pm/) · [Email](mailto:Karamjeet.6613@gmail.com) · [GitHub](https://github.com/karamjeetsingh-ai-pm)

---

<div align="center">
  <sub>✦ Part of the Astra AI Platform · Gemini · Groq · LangChain ReAct · Supabase · Tavily · Streamlit</sub>
</div>
