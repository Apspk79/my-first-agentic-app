# My agent: IT Support & Knowledge Base Assistant

One-liner: A conversational IT support agent that helps employees troubleshoot tech issues, look up solutions from a knowledge base, and manage IT support tickets.

Tool coverage:
- Memory: Remembers employee device specs (OS, hardware model), past support tickets, and recurring issues across sessions.
- Tools: Knowledge base lookup (`search_knowledge_base`), ticket creation & status updates (`create_ticket`, `get_ticket_status`), system diagnostic check (`run_diagnostics`).
- Catalog/UI: Dashboard catalog of active & resolved support tickets, hardware asset cards, and troubleshooting step-by-step cards (A2UI).
- Image gen: Generates visual setup/troubleshooting diagrams (e.g., cable connection guides or router LED indicator guides).
- Sandbox: Parses error logs and stack traces, computes network performance metrics, or validates shell script fixes.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch: Code sandbox for log analysis & diagnostic script execution, Cloud Trace for monitoring ticket SLA workflows.
