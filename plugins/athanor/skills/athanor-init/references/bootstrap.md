# Bootstrap Model

## Minimum viable project OS

Create only:

1. a root loader (`AGENTS.md`);
2. a project identity and source map;
3. decisions and tasks separated;
4. tool and integration registries;
5. a risk register;
6. a minimal ownership map.

Do not create departments, agents, or folders without current work to justify
them.

## Project constitution

Keep universal Athanor safety rules in the root agent instructions. Record only
project-specific non-negotiables in the `Project invariants` section of
`athanor/PROJECT.md`. Give each invariant an owner and a condition for changing
it. Do not add a separate constitution file when the project charter can remain
the canonical owner.

## Work dependencies

Use stable task IDs. A task is ready only when its referenced dependencies are
done. Keep this model in Markdown until the project has enough concurrent work
to justify a dedicated issue graph.

## Existing project rule

Map equivalent files before creating anything. A project may use `PROJECT.md`,
an RFC index, a vault, or a product spec instead of Athanor's default names.
Preserve working conventions and point to them.

## Date rule

Use `YYYY-MM-DD` in prose, filenames, logs, JSON, CSV, and generated examples.

## Source rule

Each important fact should have one canonical owner. Summaries may link to the
owner but must not become competing editable copies.
