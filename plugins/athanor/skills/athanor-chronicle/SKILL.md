---
name: athanor-chronicle
description: Teach and plan Git, GitHub, Git LFS, repository hygiene, backup, asset storage, secrets, and project preservation. Use when a user is new to version control, wants to decide what belongs in a repository, needs a safe first commit, has a large mixed workspace, or must distinguish history from backup.
---

# Athanor Chronicle

Teach the preservation model before initializing or publishing a repository.

## Explain the layers

- Git is local version history.
- GitHub is remote hosting and collaboration.
- Git LFS tracks pointers for selected large binaries.
- Asset storage holds media libraries and heavy working files.
- Backup supports restoration after loss or corruption.
- A secret manager or local environment holds credentials.

Read `references/preservation-model.md`.

## Assess

Resolve `<skill-directory>` as the directory containing this `SKILL.md`.

Run:

```bash
python <skill-directory>/scripts/repository_advisor.py <project-root> --output <report-directory>
```

Review the generated candidate groups. The script uses conservative filename,
extension, size, and path rules; it does not decide business sensitivity.

## Recommend

Classify artifacts into:

- Git normal;
- Git LFS candidate;
- asset storage;
- backup;
- local ignored;
- secret manager;
- human review.

Prefer authoritative text, code, configuration without secrets, tests, schemas,
small canonical assets, and operating documents in Git. Exclude dependencies,
builds, caches, temp files, credentials, personal scans, bulk media, and
reproducible exports by default.

## Prepare safely

Draft `.gitignore`, `.gitattributes`, and `.env.example` changes without
overwriting existing rules. Scan proposed tracked files for secret indicators
before staging.

Initializing Git is a local reversible preparation. Creating a remote, making
it public, pushing, changing branch protection, or rewriting history requires
explicit authorization.

## Deliver for a beginner

Explain:

1. what will be recoverable;
2. what remains outside Git;
3. where excluded important files will be backed up;
4. the proposed first commit;
5. the exact next command or approval.
