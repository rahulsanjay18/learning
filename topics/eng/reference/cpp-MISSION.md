# Mission: C and C++

*Drafted 2026-10-07 from the setup answers; correct anything that's off.*

## Why
Knows the syntax basics, computer architecture and OS concepts, but isn't fluent in the languages. Wants to be **good** at
C and C++, for all four uses asked about at setup:
- **ML / performance engineering:** fast numeric code, CUDA, PyTorch C++ extensions, inference engines (career).
- **Systems:** Linux systems programming, concurrency.
- **Games / engines:** the 3D chess variant from the Games major needs an engine.
- **General craft:** read and write real C/C++ codebases confidently and idiomatically.

## Success looks like
- Write C that is correct under the standard (no undefined behavior), and know *why* a given line is UB.
- Read the assembly a hot loop compiles to and explain its performance from caches and the memory hierarchy.
- Write modern C++ (RAII, value semantics, move, smart pointers, the STL, templates/concepts) that a reviewer would call idiomatic.
- Write correct multithreaded C++ (data races, the memory model, atomics, locks).
- Ship one real thing: the 3D chess engine, a CUDA kernel, or a merged open-source PR.

## Constraints
- Shared 1-hour-a-day floor across all majors. **Parked for now** (2026-10-07): may start after AWS ML, in place of it, or not at all.
- C first, then C++ (setup answer).

## Out of scope (for now)
- Embedded / bare-metal C, legacy pre-C++11 idioms, GUI frameworks.
