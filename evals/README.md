# Athanor evaluations

Run each case in `cases.json` from a fresh temporary fixture and a fresh agent
session whose working directory is that fixture. Give the agent only the natural
prompt, the fixture, and installed Athanor. Do not reveal the expected route or
rubric. Never launch a case from another project's working directory.

Record the transcript, invoked skills, tool trace, and filesystem diff.
Deterministic checks cover mutation boundaries, secret sentinels, dates,
organization-plan schema, project validation, and preservation of existing
instructions. Judgment-dependent behavior uses the shared 0–2 rubric.

A run passes at 16/20 or higher with no automatic failure. Test normal pull
requests on one supported runtime. Before a release, repeat the four cases on
Codex, Claude Code, and Antigravity.
