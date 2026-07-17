# GitPilot (v1) - Autonomous DevOps Git Assistant

An autonomous local Git agent that observes workspace changes, analyzes repository snapshots with an LLM, and automatically commits changes under strict safety policy guardrails.

## System Architecture & File Directory Map
All active agent systems are decoupled across independent modular layers:

- **`app/`** - Orchestration and main application logic.
  - **`app/graph/`** - LangGraph state machine orchestrator.
    - `builder.py` -> Compiles state workflow (`Observe -> Plan -> Execute -> Verify`).
    - `nodes.py` -> Execution steps fetching snapshots, prompting LLM, running actions, and verifying.
    - `router.py` -> Directs flow based on whether the action is a commit or finished.
  - **`app/state/`** - Execution state definitions.
    - `agent_state.py` -> Core `GitAgentState` TypedDict used by LangGraph.
    - `models.py` -> Pydantic objects (`ActionPlan`, `RepositorySnapshot`, `FileChange`).

- **`services/`** - Standalone engine utilities (Zero dependencies on LangGraph/AI).
  - `repository.py` -> `GitService` wrapping the local Git CLI safely using UTF-8.
  - `watcher.py` -> `watchdog` daemon triggering the graph dynamically on workspace events.
  - `policy.py` -> Security guardrails evaluating planned commits (scans for secret keys or debugging prints).

- **`llm/`** - AI layer (Zero dependencies on Git CLI).
  - `provider.py` -> Configures LLM clients and maps structured schema configurations.
  - `prompts.py` -> System prompt templates specifying DevOps guidelines and conventional commit rules.

- **`models/`** - Global shared models and static schemas.

## Active Feature Map
# GitPilot (v1) - Autonomous DevOps Git Assistant

An autonomous local Git agent that observes workspace changes, analyzes repository snapshots with an LLM, and automatically commits changes under strict safety policy guardrails.

## System Architecture & File Directory Map
All active agent systems are decoupled across independent modular layers:

- **`app/`** - Orchestration and main application logic.
  - **`app/graph/`** - LangGraph state machine orchestrator.
    - `builder.py` -> Compiles state workflow (`Observe -> Plan -> Execute -> Verify`).
    - `nodes.py` -> Execution steps fetching snapshots, prompting LLM, running actions, and verifying.
    - `router.py` -> Directs flow based on whether the action is a commit or finished.
  - **`app/state/`** - Execution state definitions.
    - `agent_state.py` -> Core `GitAgentState` TypedDict used by LangGraph.
    - `models.py` -> Pydantic objects (`ActionPlan`, `RepositorySnapshot`, `FileChange`).

- **`services/`** - Standalone engine utilities (Zero dependencies on LangGraph/AI).
  - `repository.py` -> `GitService` wrapping the local Git CLI safely using UTF-8.
  - `watcher.py` -> `watchdog` daemon triggering the graph dynamically on workspace events.
  - `policy.py` -> Security guardrails evaluating planned commits.
  - `commit_risk.py` -> Analyzes deployment risk of a specific commit hash.

- **`llm/`** - AI layer (Zero dependencies on Git CLI).
  - `provider.py` -> Configures LLM clients and maps structured schema configurations.
  - `prompts.py` -> System and action-specific prompt templates.
