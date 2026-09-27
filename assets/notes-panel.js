// Slide-out notes drawer, one per lesson. See ../.claude/skills/teach/NOTES-PANEL-FORMAT.md.
//
// Markup contract: <div data-notes-panel data-lesson-id="0001-some-lesson"></div> — the widget
// builds its own toggle button + drawer into that element; nothing else to write per lesson.
//
// Persistence, progressive enhancement: opened inside a published Claude Artifact with `db`
// granted, notes save to db.doc("notes/<lessonId>") and survive reloads, republishes, and
// sessions — the agent can also read this doc back (action "read_db") to mirror it into a local
// ./notes/<lessonId>.html file. Opened as a plain local file (any browser, any AI coding tool, or
// Claude before it's published) — no window.claude at all — falls back to localStorage: notes
// still persist across reloads, just in that one browser, never mirrored anywhere automatically.

(function () {
  const DEBOUNCE_MS = 800;

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  function buildPanel(root) {
    root.innerHTML = `
      <button class="notes-toggle" type="button" aria-expanded="false">📝 Notes</button>
      <aside class="notes-panel" hidden>
        <div class="notes-panel-head">
          <span>Notes</span>
          <button class="notes-close" type="button" aria-label="Close notes">×</button>
        </div>
        <textarea class="notes-textarea" placeholder="Jot anything here — it stays with this lesson…"></textarea>
        <div class="notes-footer">
          <span class="notes-status"></span>
          <button class="notes-copy" type="button">Copy</button>
        </div>
      </aside>
    `;
    return {
      toggle: root.querySelector(".notes-toggle"),
      panel: root.querySelector(".notes-panel"),
      close: root.querySelector(".notes-close"),
      textarea: root.querySelector(".notes-textarea"),
      status: root.querySelector(".notes-status"),
      copyBtn: root.querySelector(".notes-copy"),
    };
  }

  function setStatus(el, text, sticky) {
    el.status.textContent = text;
    if (sticky) el._lastLabel = text;
  }

  async function init(root) {
    const lessonId = root.dataset.lessonId;
    if (!lessonId) return;
    const el = buildPanel(root);

    el.toggle.addEventListener("click", () => {
      const isOpen = !el.panel.hasAttribute("hidden");
      if (isOpen) {
        el.panel.setAttribute("hidden", "");
        el.toggle.setAttribute("aria-expanded", "false");
      } else {
        el.panel.removeAttribute("hidden");
        el.toggle.setAttribute("aria-expanded", "true");
        el.textarea.focus();
      }
    });
    el.close.addEventListener("click", () => {
      el.panel.setAttribute("hidden", "");
      el.toggle.setAttribute("aria-expanded", "false");
    });
    el.copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(el.textarea.value);
        setStatus(el, "Copied");
        setTimeout(() => setStatus(el, el._lastLabel || ""), 1200);
      } catch {
        setStatus(el, "Couldn't copy");
      }
    });

    let db = null;
    if (window.claude) {
      try {
        db = await window.claude.use("db");
      } catch {
        db = null;
      }
    }

    if (db) {
      const ref = db.doc("notes/" + lessonId);
      try {
        const snap = await ref.get();
        if (snap.exists) {
          const data = snap.data();
          if (data && typeof data.text === "string") el.textarea.value = data.text;
        }
      } catch {
        setStatus(el, "Couldn't load saved notes", true);
      }
      const save = debounce(async (text) => {
        setStatus(el, "Saving…");
        try {
          await ref.set({ text, updatedAt: new Date().toISOString() });
          setStatus(el, "Saved", true);
        } catch {
          setStatus(el, "Not saved — try again", true);
        }
      }, DEBOUNCE_MS);
      el.textarea.addEventListener("input", () => save(el.textarea.value));
    } else {
      const localKey = "upskill-notes:" + lessonId;
      try {
        el.textarea.value = localStorage.getItem(localKey) || "";
      } catch {
        /* private window / blocked storage: notes just won't persist */
      }
      setStatus(el, "Saved on this device only", true);
      const save = debounce((text) => {
        try {
          localStorage.setItem(localKey, text);
          setStatus(el, "Saved on this device only", true);
        } catch {
          setStatus(el, "Not saved", true);
        }
      }, DEBOUNCE_MS);
      el.textarea.addEventListener("input", () => save(el.textarea.value));
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-notes-panel]").forEach(init);
  });
})();
