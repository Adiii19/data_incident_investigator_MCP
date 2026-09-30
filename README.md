# 🔎 Data Incident Investigator

An AI-powered incident investigation agent built with **Model Context Protocol (MCP)**, **Groq**, **Python**, and **PostgreSQL**.

The system investigates failed data pipelines by dynamically selecting MCP tools, collecting operational evidence, correlating logs, pipeline runs, dependencies, timelines, and deployments, and producing an evidence-grounded incident investigation report.

---

##  What does it do?

Instead of manually checking multiple systems when a data pipeline fails, you can ask:

> **"Investigate the customer_sync pipeline and determine why it is failing."**

The agent autonomously decides what information it needs and calls the appropriate MCP tools.

For example:

```text
User
 │
 │ "Why is customer_sync failing?"
 ▼
┌─────────────────────┐
│    Groq LLM         │
│ Investigation Agent │
└──────────┬──────────┘
           │
           │ Dynamic tool selection
           ▼
┌─────────────────────┐
│      MCP Client     │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────┐
│           MCP Server                 │
│                                      │
│  Pipeline Status                     │
│  Recent Runs                         │
│  Pipeline Logs                       │
│  Dependencies                        │
│  Incident Timeline                   │
│  Recent Deployments                  │
└──────────────────┬───────────────────┘
                   │
                   ▼
            ┌──────────────┐
            │ PostgreSQL   │
            └──────┬───────┘
                   │
                   ▼
           Investigation Evidence
                   │
                   ▼
            Final RCA Report
```

---

#  Key Features

###  AI Investigation Agent

The agent uses an LLM to determine which tools should be called during an investigation rather than following a completely hard-coded sequence.

###  Model Context Protocol

MCP provides a standardized interface between the AI agent and operational data sources.

The server exposes investigation capabilities such as:

* Pipeline status
* Recent pipeline runs
* Pipeline logs
* Pipeline dependencies
* Incident timeline
* Recent deployments
* Database health

###  Stateful Investigation

The agent maintains an `InvestigationState` containing information such as:

* Pipeline being investigated
* Iteration count
* Tools already executed
* Evidence collected
* Investigation completion state

This allows the investigation to build progressively instead of treating every tool call independently.

###  Evidence Extraction

Raw MCP responses are converted into structured evidence.

Evidence is categorized so that the final investigation can distinguish between:

```text
Evidence
Hypotheses
Tool failures
Uncertainty
```

###  Missing Evidence Detection

The system can identify potentially missing categories of evidence and provide that information back to the agent so it can decide whether additional investigation is necessary.

###  Failure Handling

Tool failures are captured rather than immediately terminating the investigation.

For example:

```text
MCP Tool
   │
   ▼
Execution Failure
   │
   ▼
ToolExecutionError
   │
   ▼
Record failure as evidence
   │
   ▼
Agent continues investigation
```

### 📊 Evidence-Grounded Final Reports

The final report is constrained to use information obtained from the investigation tools.

Reports contain:

1. Summary
2. Severity
3. Confidence
4. Evidence
5. Hypotheses
6. Recommendations
7. Uncertainty

---

#  Architecture

```text
                         ┌─────────────────┐
                         │      User       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Groq LLM     │
                         └────────┬────────┘
                                  │
                           Tool selection
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  IncidentAgent  │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
      InvestigationState   EvidenceExtractor   MissingEvidence
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   MCP Client    │
                         └────────┬────────┘
                                  │
                           Streamable HTTP
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   MCP Server    │
                         └────────┬────────┘
                                  │
                  ┌───────────────┼────────────────┐
                  │               │                │
                  ▼               ▼                ▼
              Services       Repositories     MCP Tools
                  │               │
                  └───────┬───────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ PostgreSQL  │
                   └─────────────┘
```

---

# 🧰 Technology Stack

| Technology      | Purpose                                             |
| --------------- | --------------------------------------------------- |
| Python          | Core application and agent                          |
| MCP             | Tool integration and agent-to-service communication |
| Groq            | LLM inference and tool calling                      |
| PostgreSQL      | Incident and pipeline data                          |
| SQLAlchemy      | Database access                                     |
| Docker          | PostgreSQL environment                              |
| Streamable HTTP | MCP server transport                                |
| pytest          | Testing                                             |
| uv              | Python environment and dependency management        |

---

# 🔧 MCP Tools

The investigation server exposes tools including:

### `get_pipeline_status`

Retrieves the current pipeline information and latest execution.

### `get_recent_runs`

Retrieves historical pipeline executions to identify recurring failures.

### `get_pipeline_logs`

Retrieves logs associated with pipeline execution.

### `get_pipeline_dependencies`

Identifies external systems and services that the pipeline depends on.

### `get_incident_timeline`

Reconstructs the sequence of events surrounding a pipeline failure.

### `get_recent_deployments`

Retrieves recent deployments that can be correlated with failures.

### `check_database_health`

Checks whether the application's database connection is healthy.

---

# 🔬 Example Investigation

Example question:

```text
Investigate the customer_sync pipeline and determine why it is failing.
```

The agent dynamically selected tools including:

```text
get_pipeline_status
get_recent_runs
get_pipeline_logs
get_pipeline_dependencies
get_incident_timeline
get_recent_deployments
```

The investigation correlated evidence showing:

```text
crm-service deployment
        │
        ▼
email schema changed
VARCHAR → JSONB
        │
        ▼
customer_sync transformation
expects VARCHAR
        │
        ▼
Schema mismatch
        │
        ▼
Pipeline failure
        │
        ▼
0 rows written
```

The final report then separated:

* Observed evidence
* Possible hypotheses
* Recommended actions
* Remaining uncertainty

This prevents the agent from presenting an unsupported hypothesis as an established fact.

---

# 📁 Project Structure

```text
data-incident-investigator/
│
├── src/
│   ├── incident_investigator/
│   │
│   ├── incident_agent.py
│   ├── investigation_state.py
│   ├── investigation_policy.py
│   ├── evidence_extractor.py
│   ├── missing_evidence_detector.py
│   ├── investigation_context_builder.py
│   ├── final_answer_generator.py
│   ├── final_answer_prompt.py
│   ├── context_manager.py
│   ├── tool_executor.py
│   ├── tool_result_serializer.py
│   ├── capability_registry.py
│   ├── mcp_client.py
│   ├── groq_provider.py
│   └── ...
│
├── tests/
│   └── ...
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# ⚙️ Setup

## 1. Clone the repository

```bash
git clone https://github.com/Adiii19/data_incident_investigator_MCP.git
cd data-incident-investigator
```

## 2. Create the environment

```bash
uv sync
```

Activate the environment if required by your shell.

---

## 3. Configure Groq

Set your API key as an environment variable.

### PowerShell

```powershell
$env:GROQ_API_KEY="your-api-key"
```

Do not commit API keys to the repository.

---

# 🗄️ Start PostgreSQL

The project uses Docker Compose.

```bash
docker compose up -d
```

Verify:

```bash
docker compose ps
```

The PostgreSQL container should expose:

```text
localhost:5432
```

---

# 🌐 Start the MCP Server

Run:

```bash
uv run mcp run src/incident_investigator/server.py --transport streamable-http
```

The server should start at:

```text
http://127.0.0.1:8000
```

The MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

---

# 🧪 Run the End-to-End Investigation

With PostgreSQL and the MCP server running:

```bash
uv run python src/test_end_to_end.py
```

The agent will:

```text
1. Connect to the MCP server
2. Discover available tools
3. Send the investigation request to Groq
4. Execute selected MCP tools
5. Collect evidence
6. Detect potentially missing evidence
7. Continue the investigation
8. Generate the final investigation report
```

---

# 🧪 Testing

Run the test suite with:

```bash
uv run pytest -q
```

The project includes tests for agent behavior and investigation components.

The end-to-end investigation can additionally be run against the real MCP server and PostgreSQL environment.

---

# 🔐 Design Principles

The project follows several principles intended to make the agent safer and more reliable.

### Evidence before conclusions

The agent should base conclusions on information returned by investigation tools.

### Hypotheses are not facts

Potential explanations are explicitly separated from observed evidence.

### Uncertainty is preserved

If the available evidence cannot establish a root cause, the final report should say so.

### Tool failures are observable

Tool failures become part of the investigation state instead of silently disappearing.

### Dynamic investigation

The LLM can determine which investigation capabilities are relevant instead of blindly executing every available tool.

---

# 🎯 Why MCP?

Traditional application architecture might require the AI application to contain custom integrations for every operational system.

MCP provides a standardized tool interface:

```text
AI Agent
   │
   │ MCP
   ▼
Operational Tools
   │
   ├── Pipeline system
   ├── Logs
   ├── Deployment system
   ├── Dependencies
   └── Database
```

This makes it possible to change or expand the available investigation capabilities without fundamentally redesigning the agent.

---

# 🚧 Future Improvements

Planned improvements include:

* Stronger investigation stopping criteria
* Contradictory evidence detection
* Structured confidence calculation
* Additional observability integrations
* More realistic incident datasets
* Authentication and authorization for MCP
* Persistent investigation history
* Web-based investigation dashboard
* Production deployment

---

# 📌 Project Status

**Working prototype / portfolio project**

The current implementation supports real MCP communication, LLM tool calling, PostgreSQL-backed investigation data, evidence collection, stateful investigation, failure handling, and end-to-end incident analysis.

---

## 👨‍💻 Built With

**Python · MCP · Groq · PostgreSQL · SQLAlchemy · Docker · pytest · uv**
