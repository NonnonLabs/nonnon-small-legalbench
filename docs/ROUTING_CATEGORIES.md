# Routing Categories

NONNON-small uses specialist reasoning paths behind a single public endpoint. The public route names below describe broad behavior only; this repository does not publish task-level routing tables.

| Category | Description |
|---|---|
| `DIRECT_ANSWER` | Short-answer and label-set LegalBench tasks where the final answer should be a canonical label or compact string. |
| `B1_AGENTIC_CITATION` | Citation and authority-recall tasks where case identity or citation formatting matters. |
| `B1_AGENTIC_RULE` | Rule-answering tasks requiring compact legal rule recall. |
| `B1_RULE_RECALL` | Rule-recall tasks served through the same public answer contract. |
| `B2_COT_RALPH` | Structured legal reasoning tasks where the system uses a more deliberative internal path before emitting the final answer. |
| `ROUTER_SYMBOLIC_SARA_NUMERIC` | Numeric statutory reasoning tasks handled through deterministic symbolic calculation. |

The public endpoint hides the selected route. Evaluators only need to send LegalBench prompts and score the returned answer.
