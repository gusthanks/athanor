---
name: athanor-help
description: Explain Athanor, project operations, Git, agents, memory, APIs, MCP, organization, or the next safe step in plain language. Use when a user is confused, new to AI-assisted project work, asks what a term means, wants a guided tour, or needs contextual help choosing among Athanor modules.
---

# Athanor Help

Teach in context instead of reciting the whole framework.

## Help workflow

1. Identify the exact concept or decision blocking the user.
2. Inspect the current project only when local evidence will make the
   explanation more useful.
3. Explain the concept in one short paragraph without jargon.
4. Relate it to the user's project with one concrete example.
5. State what Athanor can do automatically and what still needs the user.
6. Recommend one next safe action or one relevant module.
7. Offer deeper detail only after the immediate question is answered.

Read `references/glossary.md` when the question concerns Athanor terminology.

## Never use help to smuggle in a mutation

Do not create files, initialize Git, install a connector, or change permissions
merely because the user asked what something means. Explain first. Act only
when the request also authorizes implementation.

## Answer shape

Use:

```text
What it is:
Why it matters here:
What I recommend:
What happens next:
```

For a beginner, include copy-pasteable examples. For an expert, compress the
explanation and surface tradeoffs.
