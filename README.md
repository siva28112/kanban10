# kanban10 — IT PMO Kanban Board

![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/hosted_on-GitHub_Pages-222?logo=github)

An internal demo/training Kanban board for a fictitious bank's IT PMO. One file, no build step, no framework.

**Live demo:** https://siva28112.github.io/kanban10/

## Features
- Four columns (Backlog, In Progress, Blocked, Done) with live count badges
- Drag-and-drop plus a keyboard "Move" fallback
- Add Task form with inline validation; inline delete confirmation
- Filters by project, assignee and priority; live summary strip; overdue badges
- Email notification for new tasks via FormSubmit

## Architecture
Everything lives in `index.html` (markup, `<style>`, `<script>`).

```mermaid
flowchart LR
  UI[User action] --> Ops[addTask / moveTask / deleteTask]
  Ops --> State[(state: tasks, filters, ui)]
  State --> Render[renderBoard / renderCard]
  Render --> DOM[Board DOM]
  Ops -. new task .-> Notify[notifyNewTask]
  Notify -. POST JSON .-> FS[FormSubmit]
```

- State-driven rendering: mutate `state`, then `renderBoard()` rebuilds the DOM.
- Board events are delegated on `#board`.
- Submit is optimistic; a failed notification only shows a warning toast.
- No persistence: a refresh resets to seeded data.

## Install / run
```bash
git clone https://github.com/siva28112/kanban10.git
cd kanban10
open index.html            # or: python3 -m http.server 8765
```
To receive notifications, set `FORMSUBMIT_ENDPOINT` at the top of the script to your own address, then submit one task and click the one-time activation link FormSubmit emails you. Don't commit a real address.

## Constraints
No `localStorage`/`sessionStorage`/IndexedDB/cookies, no external resources, neutral branding. Persistence would need a backend and database with load-on-init and write-through on add/move/delete.
