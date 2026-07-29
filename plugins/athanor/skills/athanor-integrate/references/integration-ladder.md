# Integration Ladder

## Preference order

1. Use an existing manual process when volume is low and errors are costly.
2. Use an existing trusted connector when it covers the required action.
3. Use no-code automation for visible event-driven workflows.
4. Use a direct API for deterministic scheduled or server-side behavior.
5. Use MCP when an AI client needs controlled live tools or data.
6. Build a custom service or UI when authorization, policy, observability, or
   human confirmation needs infrastructure you control.

## Compare

For every option record:

- capability fit;
- account and business prerequisites;
- authentication;
- read/write surface;
- recurring and usage cost;
- rate limits and reliability;
- privacy and data residency;
- human review;
- implementation effort;
- observability;
- failure and fallback behavior;
- lock-in and portability.

## Status vocabulary

- `not-needed`
- `candidate`
- `recommended`
- `required`
- `blocked`
- `configured`
- `authenticated`
- `verified-read`
- `verified-write`
- `stale`
- `deprecated`
