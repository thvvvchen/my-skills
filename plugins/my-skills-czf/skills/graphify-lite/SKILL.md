---
name: graphify-lite
description: Convert codebases, documents, PDFs, images, or videos into a queryable knowledge graph and produce HTML, JSON, Markdown reports, and call-flow diagrams. Use when the user asks for a knowledge graph, code-structure analysis, document relationship mapping, call-chain export, or mentions graphify.
---

# Graphify Lite

Use the installed `graphify` command to map project content into a knowledge graph. This distilled skill keeps the trigger, workflow, outputs, and recovery rules from the full graphify skill.

## Workflow

1. Confirm the input scope. Analyze the current project by default; honor an explicitly supplied file or directory scope.
2. Run the basic graph build:

   ```bash
   graphify <input-path>
   ```

3. Export call relationships when requested:

   ```bash
   graphify export callflow-html
   ```

4. Inspect `graphify-out/` and report the generated files plus the most relevant findings.

## Outputs

- `graphify-out/graph.html`: interactive graph for browsing, search, and filtering.
- `graphify-out/graph.json`: complete graph data for later queries or RAG workflows.
- `graphify-out/GRAPH_REPORT.md`: concepts, relationships, unusual connections, and suggestions.
- Call-flow export: Mermaid or HTML call-chain visualization, depending on the installed version.

## Guardrails

- Confirm the input exists. Unless explicitly requested, exclude `.git`, `node_modules`, `.venv`, `dist`, caches, and generated build directories.
- Treat graph findings as leads, not proof. Verify important conclusions against source code or the original document and mention unparseable files.
- If `graphify` is not on PATH, explain that the original skill's offline wheel must be installed; do not install dependencies from the network without approval.
- On failure, preserve the error, check Python version, input path, and output permissions, then retry once.
- Read `GRAPH_REPORT.md` first, then query `graph.json` or open the HTML graph for the user's specific question. Do not dump every node without a focused need.

## Typical Uses

- Understand a new repository's modules and dependencies.
- Extract concepts and relationships from technical documentation or research material.
- Trace function calls and cross-module dependencies.
- Prepare a graph-backed RAG knowledge base.
