# Why the Today page shows what it shows (2026-10-14)

**Question:** "I didn't see the AWS placement on the Today page… it didn't show the Indian History lesson."

**Answer:** The page works as designed. Each weekday gets two majors from the `week` table in `programs.json`, and Indian History
is on **Tuesday and Saturday** only:

| Day | Block 1 | Block 2 |
|---|---|---|
| Mon | Statistics | Engineering (staff lane) |
| Tue | Statistics | **Indian History** |
| Wed | Engineering (tech lane: AWS) | Statistics |
| Thu | Engineering (interview lane) | Games |
| Fri | Statistics | Engineering (interest lane) |
| Sat | **Indian History** | Games |
| Sun | rest (review optional) | |

So on a Wednesday the page shows review → AWS placement (eng 0002) → Statistics, and no Indian History.

**How this was checked (not reasoned in prose):** I ran the page's own `planFor()` from `assets/today.js` in node against the
real `programs.json` and curricula, with your actual progress on IH 0005 (3 of 12 questions answered). Tue and Sat show
"IH100 → 0005 Cities, the Buddha and the first empire", and Wed shows eng AW000 0002 plus Statistics.

**One thing to know:** a lesson drops off the page once you've answered at least 80% of its questions or rated it at the
bottom. 3 of 12 is "in progress", so 0005 stays on your IH days until you finish it.

## Sources
- `programs.json` (`week`), `assets/today.js` (`planFor`, `blockFor`, `finished`: the 80% rule), simulated 2026-10-14.
