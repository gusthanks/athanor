# Preservation Model

## Decision questions

For each artifact family ask:

1. Is it authoritative?
2. Is it needed to understand or rebuild the project?
3. Does meaningful history justify versioning?
4. Is it reproducible?
5. Is it sensitive?
6. Is it large or binary?
7. Does it have hidden dependencies?
8. Does it need collaboration, recovery, or both?

## Default destinations

| Destination | Typical content |
|---|---|
| Git | code, Markdown, scripts, schemas, tests, small config |
| Git LFS | selected canonical binary with valuable history |
| Asset storage | media library, design sources, exports |
| Backup | all irreplaceable content |
| Secret manager | keys, tokens, passwords |
| Ignore | dependencies, cache, temp, generated output |
| Review | personal, legal, financial, or ambiguous content |

## Safety

- Private repository does not mean secret manager.
- `.gitignore` does not remove a secret already committed to history.
- Git does not replace an independent backup.
- Git LFS is selective infrastructure, not permission to version every large
  file.
- Do not rewrite shared history without a separate approved recovery plan.
