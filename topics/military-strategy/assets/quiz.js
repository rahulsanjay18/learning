// Quiz widgets with immediate feedback and a running score. No dependencies. (Adapted from topics/chess.)
// Multiple choice:  <div class="quiz" data-type="choice" data-answer="Attrition"
//                        data-options="Annihilation|Dislocation|Attrition|Exhaustion" data-hint="Ask: capacity or will?">
//                     <p class="prompt">...</p><div class="explain" hidden>...</div></div>
// Free recall:      <div class="quiz" data-type="recall"><p class="prompt">...</p>
//                     <div class="explain" hidden>model answer</div></div>
//                   The learner writes from memory, then reveals the model answer and marks themselves.
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
    if (!ok) fb.appendChild(document.createTextNode(q.dataset.hint || "Think again and try another answer."));
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

  function initRecall(q) {
    var explain = q.querySelector(".explain");
    var ta = document.createElement("textarea");
    ta.setAttribute("aria-label", "your answer");
    ta.placeholder = "Write it from memory first…";
    var reveal = document.createElement("div");
    reveal.className = "choices reveal";
    var show = document.createElement("button");
    show.type = "button"; show.textContent = "Show answer";
    reveal.appendChild(show);
    show.addEventListener("click", function () {
      explain.hidden = false;
      show.remove();
      var got = document.createElement("button"), miss = document.createElement("button");
      got.type = miss.type = "button";
      got.textContent = "I had it"; miss.textContent = "I missed some";
      [got, miss].forEach(function (b) {
        b.addEventListener("click", function () {
          record(q, b === got);
          b.classList.add(b === got ? "right" : "wrong");
          got.disabled = miss.disabled = true;
        });
        reveal.appendChild(b);
      });
    });
    q.insertBefore(ta, explain || null);
    q.insertBefore(reveal, explain || null);
  }

  function init() {
    var qs = document.querySelectorAll(".quiz[data-type]");
    total = qs.length;
    qs.forEach(function (q) { (q.dataset.type === "recall" ? initRecall : initChoice)(q); });
    if (total) {
      bar = document.createElement("div");
      bar.className = "scorebar";
      document.querySelector("main").appendChild(bar);
      updateBar();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
