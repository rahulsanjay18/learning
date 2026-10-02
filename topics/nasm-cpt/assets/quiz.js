// Quiz widgets with immediate feedback and a running score. No dependencies.
// Multiple choice:  <div class="quiz" data-type="choice" data-answer="Phase 2"
//                        data-options="Phase 1|Phase 2|Phase 3">
//                     <p class="prompt">...</p><div class="explain" hidden>...</div></div>
// Recall (number):  <div class="quiz" data-type="number" data-answer="5"><p class="prompt">...</p>
//                     <div class="explain" hidden>...</div></div>
// A first answer counts toward the score; the learner may keep trying after that.
(function () {
  var total = 0, firstTryRight = 0, answered = 0, bar;

  function updateBar() {
    if (!bar) return;
    bar.textContent = answered + " / " + total + " answered · " + firstTryRight + " right first try";
  }

  function feedback(q, ok, explain) {
    var fb = q.querySelector(".feedback");
    if (!fb) { fb = document.createElement("div"); fb.className = "feedback"; q.appendChild(fb); }
    fb.innerHTML = "";
    var v = document.createElement("span");
    v.className = "verdict " + (ok ? "ok" : "no");
    v.textContent = ok ? "Right. " : "Not quite. ";
    fb.appendChild(v);
    if (ok && explain) { fb.appendChild(explain); explain.hidden = false; }
    if (!ok) fb.appendChild(document.createTextNode("Think it through and try again."));
  }

  function record(q, ok) {
    if (q.dataset.done) return;
    q.dataset.done = "1";
    answered++;
    if (ok) firstTryRight++;
    updateBar();
  }

  function initChoice(q) {
    var answer = q.dataset.answer, explain = q.querySelector(".explain");
    var box = document.createElement("div");
    box.className = "choices";
    q.dataset.options.split("|").forEach(function (opt) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = opt;
      b.addEventListener("click", function () {
        var ok = opt === answer;
        record(q, ok);
        b.classList.add(ok ? "right" : "wrong");
        if (ok) box.querySelectorAll("button").forEach(function (x) { x.disabled = true; });
        else b.disabled = true;
        feedback(q, ok, explain);
      });
      box.appendChild(b);
    });
    q.insertBefore(box, explain || null);
  }

  function initNumber(q) {
    var answer = q.dataset.answer, explain = q.querySelector(".explain");
    var box = document.createElement("div");
    box.className = "choices";
    var input = document.createElement("input");
    input.type = "text"; input.inputMode = "numeric"; input.setAttribute("aria-label", "answer");
    var b = document.createElement("button");
    b.type = "button"; b.textContent = "Check";
    function check() {
      if (!input.value.trim()) return;
      var ok = input.value.trim() === answer;
      record(q, ok);
      input.style.borderColor = ok ? "var(--ok)" : "var(--bad)";
      if (ok) { input.disabled = true; b.disabled = true; }
      feedback(q, ok, explain);
    }
    b.addEventListener("click", check);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") check(); });
    box.appendChild(input); box.appendChild(b);
    q.insertBefore(box, explain || null);
  }

  function init() {
    var qs = document.querySelectorAll(".quiz[data-type]");
    total = qs.length;
    qs.forEach(function (q) { (q.dataset.type === "number" ? initNumber : initChoice)(q); });
    if (total) {
      bar = document.createElement("div");
      bar.className = "scorebar";
      document.querySelector("main").appendChild(bar);
      updateBar();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
