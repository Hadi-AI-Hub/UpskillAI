// Exercise tutor widget — three modes per exercise: hint, feedback on an attempt,
// and an explained full solution. See ../.claude/skills/teach/LIVE-FEEDBACK-FORMAT.md.
//
// Progressive enhancement, one codebase, no diverging versions:
//   - Opened inside a published Claude Artifact, `window.claude`'s `sample` capability
//     is live: buttons call it in-page and stream a real answer into `.tutor-feedback`.
//   - Opened as a plain local file (any browser, any AI coding tool, or Claude before
//     it's published) — no window.claude at all: buttons instead build the exact same
//     prompt and copy it to the clipboard, so the learner pastes it into whatever AI
//     assistant they have open (Claude Code, Cursor, Copilot, anything).
//
// Markup contract, once per exercise:
//   <div class="exercise">
//     <p class="task">...exercise prompt...</p>
//     <details data-hint><summary>...</summary><p>...hint text...</p></details>
//     <details data-solution><summary>...</summary><pre><code>...</code></pre><p>...note...</p></details>
//     <div class="tutor" data-tutor>
//       <textarea class="tutor-input"></textarea>
//       <div class="tutor-actions"></div>
//       <div class="tutor-feedback"></div>
//     </div>
//   </div>
// `.tutor-actions` is populated by this script — leave it empty in the HTML.

(function () {
  function exerciseData(root) {
    const exercise = root.closest(".exercise");
    const task = exercise.querySelector(".task")?.textContent.trim() || "";
    const solutionCode = exercise.querySelector("[data-solution] pre code")?.textContent.trim() || "";
    const solutionNote = exercise.querySelector("[data-solution] p")?.textContent.trim() || "";
    return { task, solutionCode, solutionNote };
  }

  function buildPrompt(action, data, attempt) {
    const { task, solutionCode, solutionNote } = data;
    if (action === "hint") {
      return `I'm working through a PySpark exercise and want a hint, not the answer.\n\nExercise: ${task}\nMy attempt so far: ${attempt || "(nothing written yet)"}\n\nGive me a concrete hint — name the specific method or concept to look at — without writing the working code or the full solution.`;
    }
    if (action === "feedback") {
      return `I'm working through a PySpark exercise and want Socratic feedback on my attempt.\n\nExercise: ${task}\nMy attempt:\n${attempt}\n\nPoint at the one biggest issue and end on a nudging question — don't just hand me the full correct solution.`;
    }
    return `I'm working through a PySpark exercise and want the full solution explained, step by step.\n\nExercise: ${task}\nReference solution:\n${solutionCode}\n${solutionNote}\n\nWalk me through why this is correct and call out the common mistakes it avoids.${attempt ? `\n\nMy own attempt was:\n${attempt}\nAlso note anything it got right or wrong.` : ""}`;
  }

  function buildSampleInput(action, data, attempt) {
    if (action === "hint") {
      return `You are a Socratic PySpark tutor. Exercise: ${data.task}\nStudent's attempt so far: ${attempt || "(nothing written yet)"}\n\nGive ONE concrete hint — name the specific method/concept to look at. Never write the working code or the full solution.`;
    }
    if (action === "feedback") {
      return `You are a Socratic PySpark tutor. Exercise: ${data.task}\nStudent's attempt:\n${attempt}\n\nFor grounding only (never quote this back verbatim), the reference solution is:\n${data.solutionCode}\n${data.solutionNote}\n\nCritique the student's attempt: point at the one biggest issue and end on a nudging question. Never reveal the full correct solution outright.`;
    }
    return `You are a PySpark tutor. Exercise: ${data.task}\nReference solution:\n${data.solutionCode}\n${data.solutionNote}\n\nWalk the student through why this is correct, step by step, and call out common mistakes it avoids. Be concise.${attempt ? ` The student's own attempt was:\n${attempt}\nNote anything it got right or wrong.` : ""}`;
  }

  const LABELS = {
    hint: { live: "Get a hint", copy: "Copy hint prompt" },
    feedback: { live: "Get feedback", copy: "Copy feedback prompt" },
    solution: { live: "Explain solution", copy: "Copy solution prompt" },
  };
  const ACTIONS = ["hint", "feedback", "solution"];

  function renderButtons(root, mode) {
    root.querySelector(".tutor-actions").innerHTML = ACTIONS.map(
      (a) => `<button class="tutor-btn" data-action="${a}">${LABELS[a][mode]}</button>`
    ).join("");
  }

  function setFeedback(el, text, cls) {
    el.textContent = text;
    el.className = "tutor-feedback" + (cls ? " " + cls : "");
  }

  function wireCopyMode(root) {
    renderButtons(root, "copy");
    if (!root.querySelector(".tutor-offline-note")) {
      const note = document.createElement("p");
      note.className = "tutor-offline-note";
      note.textContent =
        "No embedded AI here — click a button to copy a ready-made prompt, then paste it into your AI assistant (Claude Code, Cursor, Copilot, whatever you use).";
      root.querySelector(".tutor-actions").insertAdjacentElement("beforebegin", note);
    }

    const textarea = root.querySelector(".tutor-input");
    const feedback = root.querySelector(".tutor-feedback");
    const data = exerciseData(root);

    root.querySelector(".tutor-actions").addEventListener("click", async (e) => {
      const btn = e.target.closest("button[data-action]");
      if (!btn) return;
      const action = btn.dataset.action;
      const attempt = textarea.value.trim();
      if (action === "feedback" && !attempt) {
        setFeedback(feedback, "Write your attempt above first — feedback needs something to look at.", "error");
        return;
      }
      try {
        await navigator.clipboard.writeText(buildPrompt(action, data, attempt));
        setFeedback(feedback, "Copied — paste it into your AI assistant.", "copied");
      } catch {
        setFeedback(feedback, "Couldn't copy — select and copy the prompt manually.", "error");
      }
    });
  }

  function wireLiveMode(root, sample) {
    renderButtons(root, "live");
    const textarea = root.querySelector(".tutor-input");
    const feedback = root.querySelector(".tutor-feedback");
    const data = exerciseData(root);
    const actionsEl = root.querySelector(".tutor-actions");

    actionsEl.addEventListener("click", async (e) => {
      const btn = e.target.closest("button[data-action]");
      if (!btn) return;
      const action = btn.dataset.action;
      const attempt = textarea.value.trim();
      if (action === "feedback" && !attempt) {
        setFeedback(feedback, "Write your attempt above first — feedback needs something to look at.", "error");
        return;
      }
      const buttons = Array.from(actionsEl.querySelectorAll("button"));
      buttons.forEach((b) => (b.disabled = true));
      setFeedback(feedback, "Thinking…", "pending");
      try {
        const input = buildSampleInput(action, data, attempt);
        const result = await sample(input, {
          onText: ({ text }) => setFeedback(feedback, text, "pending"),
        });
        setFeedback(feedback, result.text, "done");
      } catch (err) {
        if (err && err.code === "not_granted") {
          setFeedback(feedback, "Live AI was declined for this session — reload the lesson to use the copy-a-prompt fallback instead.", "offline");
        } else if (err && err.code === "rate_limited") {
          setFeedback(feedback, "Rate limited — try again in a moment.", "error");
        } else {
          setFeedback(feedback, "Couldn't reach the live tutor — try again.", "error");
        }
      } finally {
        buttons.forEach((b) => (b.disabled = false));
      }
    });
  }

  async function init(root) {
    let sample = null;
    if (window.claude) {
      try {
        sample = await window.claude.use("sample");
      } catch {
        sample = null;
      }
    }
    if (sample) {
      wireLiveMode(root, sample);
    } else {
      wireCopyMode(root);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-tutor]").forEach(init);
  });
})();
