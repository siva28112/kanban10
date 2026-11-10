# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A single-file IT PMO Kanban demo (fictitious bank, internal training tool): everything lives in `index.html` (markup, `<style>`, `<script>`). No build, lint, or test tooling exists.

## Running

- Open `index.html` directly (double-click / `file://`). No server is required.
- The built-in browser pane renders `file://` pages as static snapshots without running scripts, so to test interactively serve it: `python3 -m http.server 8765` from this folder, then open `http://localhost:8765/index.html`. Stop the server when done.

## Hard constraints (from the original spec)

- Vanilla HTML/CSS/JS only: no frameworks, CDNs, fonts, images, or build step. System font stack, inline glyphs only.
- No persistence of any kind: no `localStorage`, `sessionStorage`, IndexedDB, or cookies. A refresh must reset to the seeded demo data (the UI says so).
- No `!important` in CSS; no `alert()`/`confirm()` (inline UI only).
- Use a neutral "IT PMO" text wordmark and blue palette; no real bank logos or branding. Task IDs still use the spec'd `UOB-ITPM-####` format via the `ID_PREFIX` constant.
- The only network call is the FormSubmit AJAX POST in `notifyNewTask()`. The email address must appear only in `FORMSUBMIT_ENDPOINT` (config block at the top of the script, with the activation comment above it).

## Architecture

- `state = { tasks, filters, ui }` is the single source of truth. All DOM for the summary strip, columns and cards is rebuilt by `renderBoard()` / `renderCard()`; mutate `state` then re-render, never edit card DOM directly. Transient UI state (e.g. which card shows "Delete? Yes/No") lives in `state.ui` for this reason.
- Data ops (`addTask`, `moveTask`, `deleteTask`, `applyFilters`) are the only mutators/readers of `state.tasks`. Filters are applied at render time; the summary strip counts ALL tasks, while column badges count filtered tasks.
- Board events (drag/drop, Move ▸ select, delete buttons) are delegated on `#board`, because the board innerHTML is replaced on every render. Don't attach listeners to individual cards.
- All user-supplied strings must go through `escapeHtml()` before being placed in HTML strings.
- Add Task form: field IDs in `FIELDS` must each have a matching `<id>Err` element (e.g. `descriptionErr`); `setError()` throws and aborts init if one is missing. Submit is optimistic: the card is added and rendered first, then `notifyNewTask()` runs in try/catch and only produces a warning toast on failure.
- Dates are `YYYY-MM-DD` strings compared lexically against `todayISO()` (local time); seed due dates are offsets from today so overdue examples stay overdue.
