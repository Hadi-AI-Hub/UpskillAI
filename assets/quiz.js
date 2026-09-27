// Shared quiz widget. Markup contract:
// <div class="quiz-q" data-answer="2">
//   <p class="prompt">...</p>
//   <ul class="quiz-choices">
//     <li><button>choice A</button></li>
//     <li><button>choice B</button></li>
//     ...
//   </ul>
//   <p class="quiz-feedback"></p>
// </div>
// data-answer is the 0-based index of the correct choice.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".quiz-q").forEach((q) => {
    const correctIdx = parseInt(q.dataset.answer, 10);
    const buttons = Array.from(q.querySelectorAll(".quiz-choices button"));
    const feedback = q.querySelector(".quiz-feedback");
    buttons.forEach((btn, i) => {
      btn.addEventListener("click", () => {
        if (btn.disabled) return;
        buttons.forEach((b) => (b.disabled = true));
        if (i === correctIdx) {
          btn.classList.add("correct");
          feedback.textContent = "Correct.";
          feedback.className = "quiz-feedback correct";
        } else {
          btn.classList.add("incorrect");
          buttons[correctIdx].classList.add("correct");
          feedback.textContent = "Not quite — correct answer highlighted.";
          feedback.className = "quiz-feedback incorrect";
        }
      });
    });
  });
});
