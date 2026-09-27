// Lesson-completion button. See ../.claude/skills/teach/LESSON-COMPLETE-FORMAT.md.
//
// Markup contract: <div data-lesson-complete data-lesson-id="0001-some-lesson"></div> — builds
// its own button into that element.
//
// Persistence, progressive enhancement: opened inside a published Claude Artifact with `db`
// granted, writes/reads db.doc("completion/<lessonId>") — the agent can read this back (action
// "read_db") to know a lesson is done without asking in chat. Opened as a plain local file (any
// browser, any AI coding tool, or Claude before it's published) — no window.claude at all — falls
// back to localStorage: the button still works fully, it's just a personal per-browser reminder
// an agent can't read back, so telling the agent in chat remains how "done" gets reported there.

(function () {
  function render(root, state) {
    // state: "idle" | "done"
    if (state === "done") {
      root.innerHTML = `
        <button class="lesson-complete-btn done" type="button">✓ Lesson complete</button>
        <button class="lesson-complete-undo" type="button">Not done yet — undo</button>
      `;
    } else {
      root.innerHTML = `<button class="lesson-complete-btn" type="button">Mark this lesson complete</button>`;
    }
  }

  async function init(root) {
    const lessonId = root.dataset.lessonId;
    if (!lessonId) return;

    let db = null;
    if (window.claude) {
      try {
        db = await window.claude.use("db");
      } catch {
        db = null;
      }
    }

    if (db) {
      const ref = db.doc("completion/" + lessonId);
      let isDone = false;
      try {
        const snap = await ref.get();
        isDone = snap.exists && snap.data() && snap.data().completed === true;
      } catch {
        /* treat as not-done; the button still works going forward */
      }
      render(root, isDone ? "done" : "idle");
      wireDb(root, ref);
    } else {
      const key = "upskill-complete:" + lessonId;
      let isDone = false;
      try {
        isDone = localStorage.getItem(key) === "true";
      } catch {
        /* private window / blocked storage: button still works, just won't persist */
      }
      render(root, isDone ? "done" : "idle");
      root.insertAdjacentHTML(
        "beforeend",
        `<p class="lesson-complete-offline">Saved on this device only — tell your agent in chat when you're done, this button doesn't report anywhere.</p>`
      );
      wireLocal(root, key);
    }
  }

  function wireDb(root, ref) {
    const btn = root.querySelector(".lesson-complete-btn");
    const undoBtn = root.querySelector(".lesson-complete-undo");
    if (btn && !btn.classList.contains("done")) {
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.textContent = "Marking…";
        try {
          await ref.set({ completed: true, completedAt: new Date().toISOString() });
          render(root, "done");
          wireDb(root, ref);
        } catch {
          btn.disabled = false;
          btn.textContent = "Couldn't save — try again";
        }
      });
    }
    if (undoBtn) {
      undoBtn.addEventListener("click", async () => {
        undoBtn.disabled = true;
        try {
          await ref.set({ completed: false, completedAt: new Date().toISOString() });
          render(root, "idle");
          wireDb(root, ref);
        } catch {
          undoBtn.disabled = false;
        }
      });
    }
  }

  function wireLocal(root, key) {
    const btn = root.querySelector(".lesson-complete-btn");
    const undoBtn = root.querySelector(".lesson-complete-undo");
    if (btn && !btn.classList.contains("done")) {
      btn.addEventListener("click", () => {
        try {
          localStorage.setItem(key, "true");
        } catch {
          /* not persisted this time, but still reflect the click */
        }
        render(root, "done");
        root.insertAdjacentHTML(
          "beforeend",
          `<p class="lesson-complete-offline">Saved on this device only — tell your agent in chat when you're done, this button doesn't report anywhere.</p>`
        );
        wireLocal(root, key);
      });
    }
    if (undoBtn) {
      undoBtn.addEventListener("click", () => {
        try {
          localStorage.setItem(key, "false");
        } catch {
          /* ignore */
        }
        render(root, "idle");
        root.insertAdjacentHTML(
          "beforeend",
          `<p class="lesson-complete-offline">Saved on this device only — tell your agent in chat when you're done, this button doesn't report anywhere.</p>`
        );
        wireLocal(root, key);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-lesson-complete]").forEach(init);
  });
})();
