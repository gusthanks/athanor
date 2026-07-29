---
name: athanor-integrate
description: Guide a user from a desired outcome to the right manual workflow, connector, no-code automation, direct API, MCP server, plugin, or scheduled process. Use when a project needs external data or actions, the user asks what to connect, or setup requires prerequisites, authentication, permissions, cost, testing, and fallbacks explained clearly.
---

# Athanor Integrate

Choose the smallest capability layer that achieves the outcome.

## Start from the outcome

Clarify:

1. what should happen;
2. who initiates it;
3. whether it is manual, conversational, scheduled, or event-driven;
4. what data is read or written;
5. who owns the external account;
6. cost, privacy, reliability, and review requirements.

Read `references/integration-ladder.md`.

## Compare paths

Evaluate:

- manual AI-assisted workflow;
- existing connector or plugin;
- no-code automation;
- direct API or webhook;
- MCP exposed to an AI client;
- custom service or UI.

Do not recommend MCP merely because AI participates. A scheduler or direct API
may be the correct execution layer while MCP provides optional conversational
control.

## Verify current provider facts

Provider permissions, policies, pricing, endpoints, review requirements, and
account prerequisites are temporally unstable. Verify current official
documentation before giving exact setup steps. Record the verification date and
source.

## Produce an integration card

Use `assets/integration-card.md`. Include purpose, owner, status, authentication,
read/write scope, human steps, agent steps, cost, risk, test, fallback, and
last verification.

Never put token values or credentials in the card.

## Gate mutations

Reading public documentation is safe. Account creation, OAuth authorization,
permission expansion, paid activation, external writes, and production
automation require explicit authorization at the exact step.

Test read capability before write capability. Test writes in draft, sandbox, or
private scope when the provider supports it.
