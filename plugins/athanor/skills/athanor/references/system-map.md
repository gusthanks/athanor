# Athanor System Map

## Components

| Component | Purpose |
|---|---|
| Skill | Reusable method and instructions |
| Project OS | Durable context generated inside a project |
| Agent | Bounded responsibility and operating contract |
| Memory | Verified learning and decisions across sessions |
| Runtime | Host that executes agents, such as Codex or Claude |
| MCP/API | Live capability or external data connection |
| Automation | Scheduled or event-triggered execution |
| Hook | Mechanical lifecycle enforcement |

## Risk gates

Escalate to Guardian behavior when a task touches money, publication, deletion,
credentials, production, legal obligations, health, minors, employee data,
customer identity, or secret business information.

Guardian behavior means:

1. verify the current authoritative source;
2. state the proposed action and impact;
3. separate reversible preparation from the gated mutation;
4. request approval only for the exact action;
5. verify the result after execution;
6. record the decision or incident in the appropriate project file.

## Operating axes

Collaboration style controls how much the user participates:

- `scribe` — proposal-first;
- `alchemist` — recommendation and dialogue;
- `adept` — autonomous reversible work inside known boundaries.

Assurance controls the depth of verification:

- `lean` — proportional checks for low-risk work;
- `standard` — verify important assumptions and outcomes;
- `guardian` — authoritative evidence, adversarial review, and an audit trail.

The axes combine. `adept + guardian`, for example, prepares and verifies
autonomously but still stops at an approval gate. Risk can elevate effective
assurance; it cannot grant authority.

## Routing order

1. Audit an unknown workspace.
2. Bootstrap missing governance.
3. Organize only after ownership and purpose are understood.
4. Chronicle authoritative material before risky structural changes.
5. Design agents after responsibilities exist.
6. Integrate tools after the outcome and owner are known.
7. Maintain continuously.
