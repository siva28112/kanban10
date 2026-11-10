#!/usr/bin/env python3
"""
PostToolUse hook (Edit|Write): make sure index.html contains the IT-meeting
reminder popup. If a visitor stays on the page for more than 10 seconds, an
accessible in-page dialog announces the meeting. The script is idempotent: it
only touches index.html when the marked blocks are missing.

Claude Code passes the tool call as JSON on stdin. Hooks cannot observe website
visitors; the popup logic lives in index.html and this hook just keeps it there.
"""
import json, os, sys

MEETING_TEXT = "IT meeting next Wednesday, 10:00 AM, Room 888"
DELAY_SECONDS = 10

CSS = """/*MEETING-POPUP:CSS*/
.meeting-backdrop { position: fixed; inset: 0; z-index: 30; display: none; align-items: center; justify-content: center; padding: var(--sp-4); background: var(--overlay); backdrop-filter: blur(3px); }
.meeting-backdrop.open { display: flex; }
.meeting-dialog { width: 100%; max-width: 420px; background: var(--surface); color: var(--text); border-radius: 20px; padding: var(--sp-5); box-shadow: var(--shadow-lift); text-align: center; animation: pop 0.25s ease both; }
.meeting-dialog .m-icon { width: 56px; height: 56px; margin: 0 auto var(--sp-3); border-radius: 18px; display: grid; place-items: center; color: #fff; background: linear-gradient(135deg, #5b4bff, #00a3d9); }
.meeting-dialog h2 { margin: 0 0 var(--sp-2); font-size: 20px; }
.meeting-dialog p { margin: 0 0 var(--sp-4); color: var(--muted); }
.meeting-dialog .m-detail { display: grid; gap: var(--sp-1); margin-bottom: var(--sp-4); font-weight: 700; }
/*MEETING-POPUP:CSS-END*/
"""

HTML = """<!--MEETING-POPUP:HTML-->
<div class="meeting-backdrop" id="meetingPopup">
  <section class="meeting-dialog" role="alertdialog" aria-modal="true" aria-labelledby="meetingTitle" aria-describedby="meetingText">
    <div class="m-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg></div>
    <h2 id="meetingTitle">Meeting reminder</h2>
    <p id="meetingText">Please join the next IT team meeting.</p>
    <div class="m-detail"><span>Next Wednesday, 10:00 AM</span><span>Room 888</span></div>
    <button type="button" class="btn btn-primary" id="meetingOk">Got it</button>
  </section>
</div>
<!--MEETING-POPUP:HTML-END-->
"""

JS = """/*MEETING-POPUP:JS*/
(function initMeetingPopup() {
  const DELAY_MS = %d * 1000;
  const popup = document.getElementById("meetingPopup");
  const ok = document.getElementById("meetingOk");
  if (!popup || !ok) return;
  let visibleMs = 0, last = Date.now(), shown = false, lastFocus = null;
  function open() {
    shown = true;
    lastFocus = document.activeElement;
    popup.classList.add("open");
    ok.focus();
  }
  function close() {
    popup.classList.remove("open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  // Counts only time the tab is visible; the popup shows once per page load.
  const timer = setInterval(function () {
    const now = Date.now();
    if (!document.hidden) visibleMs += now - last;
    last = now;
    if (!shown && visibleMs > DELAY_MS) { clearInterval(timer); open(); }
  }, 500);
  ok.addEventListener("click", close);
  popup.addEventListener("mousedown", function (e) { if (e.target === popup) close(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && popup.classList.contains("open")) close();
  });
})();
/*MEETING-POPUP:JS-END*/
""" % DELAY_SECONDS

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    path = (payload.get("tool_input") or {}).get("file_path", "")
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    target = os.path.join(project, "index.html")
    # Only react to edits of index.html (or manual runs with no payload).
    if path and os.path.basename(path) != "index.html":
        return 0
    if not os.path.isfile(target):
        return 0
    with open(target, encoding="utf-8") as f:
        src = f.read()
    out = src
    if "/*MEETING-POPUP:CSS*/" not in out and "</style>" in out:
        out = out.replace("</style>", CSS + "</style>", 1)
    if "<!--MEETING-POPUP:HTML-->" not in out and "<!-- ===== Toast region" in out:
        out = out.replace("<!-- ===== Toast region", HTML + "\n<!-- ===== Toast region", 1)
    if "/*MEETING-POPUP:JS*/" not in out and "</script>" in out:
        i = out.rindex("</script>")
        out = out[:i] + "\n" + JS + out[i:]
    if out != src:
        with open(target, "w", encoding="utf-8") as f:
            f.write(out)
        print(json.dumps({"systemMessage": "meeting-popup hook: restored the IT meeting popup in index.html"}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
