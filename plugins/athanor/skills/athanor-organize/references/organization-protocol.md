# Organization Protocol

## Taxonomy rules

- Choose one semantic axis per folder level.
- Organize by what an artifact is or serves, not by vendor, extension, or
  temporary status.
- Keep source and export relationships discoverable.
- Prefer the existing coherent convention over a generic template.
- Use one triage location for future ambiguous captures.

## Inspection tiers

1. Path, extension, size, timestamps, and metadata.
2. Extracted text and document headings.
3. OCR or contact-sheet preview.
4. Detailed vision for unresolved visual assets.
5. Human classification when confidence remains low.

## Manifest schema

Required CSV columns (copy `assets/organization-plan.csv` when useful):

```text
id,source,destination,action,reason,confidence,risk,approved
```

Allowed actions:

- `move`
- `rename`
- `mkdir`
- `review`
- `skip`

Only `move` and `rename` are applied by the script. `mkdir` is implicit when
needed. `review` and `skip` are never mutated.

`approved` must be exactly `true` for application.

## Automatic high-risk cases

- InDesign, Illustrator, Photoshop, DAW, CAD, video, or 3D project sources;
- files referenced by code, HTML, CSS, Markdown, manifests, or build systems;
- nested Git repositories;
- symlinks and junctions;
- encrypted, personal, legal, financial, or credential-related material;
- paths already participating in deployment or automation.

High-risk rows require human review even with the Adept collaboration style.

## Naming

Default dated prefix: `YYYY-MM-DD`.

Recommend ASCII kebab-case for web and automation assets, but do not rename a
codebase or established production pipeline merely to enforce this preference.
