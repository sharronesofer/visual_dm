# Interaction System Architectural Decisions: Extraction Summary

This document summarizes all architectural decisions extracted from Q&A sessions, technical review notes, meeting minutes, and design documents for the Interaction System. Each decision is referenced by its Decision ID and links to the detailed spreadsheet (`interaction_system_arch_decisions.xlsx`).

## Categories

- Data Flow Architecture
- Component Interaction Patterns
- State Management Approach
- Threading and Concurrency Model
- Error Handling Strategy
- Extensibility Mechanisms
- Integration with Other Game Systems

---

## Decision Summary Table

| Decision ID | Category | Problem/Question | Chosen Solution | Source Reference | Status |
|-------------|----------|------------------|-----------------|------------------|--------|
|             |          |                  |                 |                  |        |
|             |          |                  |                 |                  |        |

---

## Source Materials

All source documents used for extraction are stored in `/docs/architecture/source_materials/`.

## Notes
- For full details and rationale, see the spreadsheet: [`interaction_system_arch_decisions.xlsx`](interaction_system_arch_decisions.xlsx)
- Ambiguous or pending decisions are flagged for follow-up in the next documentation phase.

---

## Pending Architectural Decisions

The following architectural questions or decisions remain unresolved and require further discussion or action before play-testing. This list was compiled via a comprehensive gap analysis of all ADRs, technical requirements (see `undocumented_requirements.md`), feature prioritization summaries, and supporting diagrams. Items are prioritized by criticality for play-testing and cross-referenced with source documents. High-priority items are highlighted for immediate follow-up.

| Pending ID | Question/Problem | Why Unresolved | Options Considered | Dependencies | Impact if Unresolved | Timeline | Priority |
|------------|------------------|---------------|--------------------|--------------|---------------------|----------|----------|
| P-001 | Input handling extensibility for new device types (e.g., VR, future controllers) | Current implementation supports keyboard/controller/touch, but lacks abstraction for future device integration | 1. Abstract input layer now; 2. Defer until new device needed | IR-001, InputHandler module | May block accessibility or future platform support | Before play-testing on new platforms | High |
| P-002 | Multi-step/chained interaction logic and conditional flows | Design for multi-step/conditional interactions not finalized; unclear how to represent in state and UI | 1. State machine per interaction; 2. Scripting system; 3. Hardcoded logic | IR-003, InteractionManager, UI | Limits complex gameplay scenarios, may block advanced play-testing | Prototype before advanced play-testing | High |
| P-003 | Edge case feedback (overlapping interactables, multiplayer, progression resets) | Edge case handling logic not fully specified; UI/UX for feedback not finalized | 1. Contextual UI overlays; 2. Event log; 3. Minimal feedback | IR-005, UI, EventBus | May cause confusion or missed interactions during play-testing | Before multiplayer/edge-case play-tests | High |
| P-004 | Profiling and optimization for large numbers of interactables | Profiling tools and optimization strategies not fully integrated; performance under load untested | 1. Integrate profiling tools now; 2. Optimize reactively | IR-006, EventBus, InteractionManager | Risk of poor performance/scalability in large scenes | Before large-scale play-testing | High |
| P-005 | Standardized error codes/messages and separation of user/system logs | Error handling framework partially implemented; not all APIs/events use standard codes | 1. Enforce standardization now; 2. Gradual migration | IR-007, Error Handling, Logging | Inconsistent error reporting, harder debugging | Before public play-testing | Medium |
| P-006 | Event-driven architecture for state changes: async safety and transaction boundaries | EventBus async safety and transactionality not fully validated; risk of race conditions | 1. Add transactional event wrappers; 2. Accept eventual consistency | IR-008, EventBus, StateController | Potential for state desync or bugs in edge cases | Before integration with other systems | High |
| P-007 | Logging system: structured JSON logs, correlation IDs | Logging partially structured; correlation IDs not consistently applied | 1. Enforce structured logging everywhere; 2. Add correlation ID middleware | IR-009, Logging, EventBus | Harder to trace/debug issues in play-testing | Before play-testing | Medium |
| P-008 | Integration with Dialogue, Memory, POI Evolution systems | Some integration points defined, but not all data models/events finalized | 1. Finalize shared models now; 2. Integrate iteratively | IR-010, EventBus, Data Models | May block cross-system features in play-testing | Before cross-system play-testing | High |
| P-009 | Missing/undocumented ADRs for data flow, component interaction, state management | ADRs referenced in index but not present; some decisions only in summary | 1. Write missing ADRs; 2. Consolidate in summary | ADR Index, Summary | Gaps in traceability, onboarding, and review | Before final documentation | High |
| P-010 | Diagrams: ensure all referenced diagrams are up to date and cover new/changed flows | Diagrams present but may not reflect latest changes or edge cases | 1. Update diagrams now; 2. Defer until after implementation | Diagrams, ADRs | Outdated diagrams may mislead implementers | Before documentation freeze | Medium |

- Each pending decision is cross-referenced with relevant ADRs, requirements, or diagrams.
- High-priority items (Priority = High) require immediate follow-up before play-testing.
- This section will be reviewed and updated as decisions are made or new gaps are identified.
