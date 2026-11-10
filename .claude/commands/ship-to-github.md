---
description: Push this project to GitHub, document it, publish GitHub Pages, add CI/CD and run a security scan
argument-hint: <owner/repo or https://github.com/owner/repo.git> [branch]
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Ship to GitHub

Repo info supplied by the user: `$ARGUMENTS`

If `$ARGUMENTS` is empty or does not identify a repo (`owner/repo` or a GitHub URL), ask the user for the repo and optional branch (default `main`) before doing anything else.

This project is a single-file vanilla HTML/CSS/JS app (`index.html`) with no build step. Read `CLAUDE.md` and `index.html` first so the README and workflow match reality.

Work through the steps in order. Report each step's outcome faithfully; if a step fails or is skipped, say so. Pushing, changing repo settings and publishing Pages are outward-facing: show the user the exact repo, branch and files that will be pushed and get a clear yes before step 1's push and before step 4.

## 0. Security scan first (gate)

Run this before anything leaves the machine. If it finds a problem, stop and report; do not push.

1. Search the project for secrets and personal data: API keys, tokens, passwords, private keys, `.env` files, real email addresses, phone numbers. Use Grep with patterns such as `AKIA`, `ghp_`, `sk-`, `BEGIN .*PRIVATE KEY`, `password\s*=`, `secret`, `token`, and an email regex.
2. Confirm the only email-like value is the placeholder in `FORMSUBMIT_ENDPOINT` (`YOUR_EMAIL@example.com`). A real address must never be committed. If one is present, replace it with the placeholder and tell the user.
3. Check that nothing sensitive is sent to the internet:
   - Grep for `fetch(`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `<script src`, `<link href="http`, `@import`, `http://`, `https://`. The only allowed outbound call is the FormSubmit POST in `notifyNewTask()`, and its payload must contain only task fields (ID, title, description, project, category, assignee, priority, due date, status, timestamp).
   - Confirm no analytics, CDN, font or tracker references, and no `localStorage`, `sessionStorage`, `indexedDB` or `document.cookie`.
4. Make sure `.gitignore` exists and excludes `.env*`, `.DS_Store`, `.claude/settings.local.json`, `node_modules/`.
5. Check git history if a repo already exists (`git log -p` grep for the same patterns).
6. Write a short findings summary (clean / issues with file:line).

## 1. Push the code

1. If this folder is not a git repo, `git init` and `git branch -M <branch>`.
2. Show `git status` and the file list to be committed. Do not commit `.claude/settings.local.json` or local scratch files.
3. Commit with a clear message.
4. Add or update `origin` to the supplied repo, then `git push -u origin <branch>`.
5. Use the `gh` CLI where possible. If the repo does not exist, ask before creating it, and ask whether it should be public or private.

## 2. README

Create or edit `README.md` (keep any user-written content; edit rather than overwrite). Include:

- Title and one-line description (internal demo/training IT PMO Kanban board for a fictitious bank).
- Tech badges (shields.io static badges): HTML5, CSS3, JavaScript, GitHub Pages, GitHub Actions, no-dependencies.
- Live demo link (filled in after step 4).
- Features list.
- Architecture: the single-file structure, state-driven `renderBoard()` flow, delegated board events, FormSubmit notification path, no-persistence design. A Mermaid diagram is welcome.
- How to install/run: clone, double-click `index.html`, or `python3 -m http.server 8765`. Mention setting `FORMSUBMIT_ENDPOINT` and the one-time FormSubmit activation email.
- Notes on constraints (no storage, refresh resets, neutral branding) and a short note on what persistence would require.

## 2b. Screenshot (Playwright MCP)

Requires Node.js and the project-level `playwright` MCP server from `.mcp.json`. If its tools are not available, tell the user to install Node.js and restart the session; do not substitute a mock image.

1. Serve the app locally (`python3 -m http.server 8765` in the background) and open `http://localhost:8765/index.html` with the Playwright MCP tools. Scripts must run, so do not use `file://` snapshots.
2. Wait for the seeded cards to render, then take a full-page screenshot and save it as `docs/screenshot.png` (create `docs/`). Verify the file exists and is a non-empty PNG.
3. Add it to `README.md` under the title: `![IT PMO Kanban board](docs/screenshot.png)`. Commit it with the README.
4. If `PP_Assessment_Task1_Completed.docx` exists in the project root, paste the screenshot into the empty answer box under **Task 2 (A2)** ("Paste your screenshot in the box below"), at a width that fits the page (about 6 inches), without changing other content. Edit a copy first, check the result opens and the Task 1 image is intact, then replace the original. Never commit the .docx. If the design has not been improved with an Agent Skill, tell the user the screenshot does not yet satisfy A2's "redesigned site" wording.
5. Stop the local server.

## 3. GitHub About section

Set description, topics and homepage with `gh repo edit <owner/repo>`:

- Description: short summary of the app.
- Topics: e.g. `kanban`, `project-management`, `vanilla-javascript`, `html5`, `css3`, `drag-and-drop`, `github-pages`, `demo`.
- Homepage: left for step 5.

## 4. GitHub Pages

1. Ask for confirmation, then enable Pages. Prefer deployment via GitHub Actions (`gh api -X POST repos/<owner/repo>/pages -f build_type=workflow`), or serve from the `main` branch root if Actions deployment is not possible.
2. Wait for the first deployment and confirm the URL (`https://<owner>.github.io/<repo>/`) returns HTTP 200.

## 5. Add the Pages URL to About

Run `gh repo edit <owner/repo> --homepage <pages-url>`, then put the same URL in the README live demo link and push that change.

## 6. CI/CD with GitHub Actions

Create `.github/workflows/ci.yml` (and `pages.yml` if you use Actions deployment):

- Triggers: `push` and `pull_request` on the default branch; use least-privilege `permissions`.
- CI job: checkout, then checks that fit a no-build project: HTML validation (e.g. `html5validator` or `tidy`), a grep guard that fails on `localStorage|sessionStorage|indexedDB|document.cookie|!important`, a guard that fails if any URL other than the FormSubmit endpoint appears in `index.html`, and a secret scan (e.g. gitleaks action).
- Deploy job (main only): `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`, with `pages: write` and `id-token: write`.
- Pin third-party actions to a major version or SHA.

After pushing, check the run with `gh run list` / `gh run watch` and fix failures.

## Final report

List: scan result, repo URL, commit/branch pushed, README changes, About description/topics/homepage, Pages URL and status, workflow files and their latest run status, and anything skipped or still needing the user (for example FormSubmit activation, or setting the real email only locally).
