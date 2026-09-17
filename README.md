# File-Based Key-Value Store — Build Notes

A small CLI key-value store built to practice decorators, generators, and context managers together in one real piece of code — not in isolation. This README documents the actual bugs hit while building it, because most of the learning happened in fixing them, not in the first draft.

## What it does

```
python main.py set <key> <value>
python main.py get <key>
python main.py delete <key>
python main.py list
```

Data persists to a text file (`dummy_key_val.txt`), every operation is timed and logged to `logs.txt`, and file lifecycle (loading on start, writing back on exit) is handled by a custom context manager.

## Bugs found and fixed, in the order they came up

### 1. Decorator silently discarded return values
Original `wrapper` called `func(*args, **kwargs)` but never captured or returned the result. Every decorated function — including `get()` — returned `None` to its caller regardless of what it actually computed internally. Fixed by capturing `res = func(...)` and explicitly returning it.

### 2. Missing `functools.wraps`
Without `@wraps(func)` on the inner `wrapper`, every decorated function's `__name__`, `__doc__`, etc. got silently replaced with `wrapper`'s own metadata — breaking introspection, debugging tools, and stack traces (everything would report itself as "wrapper" instead of its real name).

### 3. Failed calls were logged as if nothing happened
The original decorator only wrote a log line *after* a successful call. If the wrapped function raised, execution jumped straight to the caller — the log line was never reached, so crashes vanished with zero trace. Fixed with `try`/`except`: log the failure, then re-raise with a bare `raise` (not `raise e`, which would rewrite the traceback).

### 4. Confusing `dict.get()` with something that raises
Tried to test the exception-logging path using `get("missing_key")`. It didn't fail — because `dict.get()` is specifically designed to return `None` on a missing key rather than raise. `del data[key]` on a missing key does raise `KeyError` — that's what actually exercised the failure path. Good reminder that not all "missing data" operations fail the same way.

### 5. Function named `set` shadowed the built-in
`def set(key, value):` silently overwrote Python's built-in `set` type for the rest of the file. Renamed to `set_val` to avoid any future collision.

### 6. `list_all()` baked `print()` into the function itself
Early version of the "list everything" function printed directly instead of yielding raw data, making it useless for any purpose other than terminal output (same root problem as bug #1, recurring in a new spot). Fixed by having the generator `yield key, val` as raw tuples and letting the caller decide what to do with them.

### 7. The generator-vs-decorator interaction — the real center of the build
This was the hardest part, and worth explaining properly rather than just listing as "fixed":

- A generator function doesn't run its body when called — it returns a generator object immediately. Calling `func()` inside a decorator's `wrapper` does **not** execute any of the function's internal logic.
- That means the original `@timed` decorator, when applied to a generator function, measured almost nothing — just the time to *create* the generator object, not the time to actually produce all its values.
- The fix required `wrapper` itself to become a generator (containing its own `yield`), looping over the wrapped generator and passing each value through, so timing could wrap the *entire* consumption, not just the instant of creation.
- **One `@timed` couldn't serve both cases.** `inspect.isgeneratorfunction(func)` is checked once, at decoration time, and `timed()` returns one of two different wrapper implementations depending on the answer.

### 8. Early abandonment of a generator (`break` mid-iteration)
If the caller stops iterating a generator early (e.g. `break`), Python throws `GeneratorExit` into the generator at its paused `yield` point — and this is deliberately **not** a subclass of `Exception`, so a plain `except Exception` never catches it. This meant any code placed "after the loop" for the success case simply never ran on early exit — and the status only reported correctly once logging was moved into a `finally` block, which runs regardless of whether the loop finished, raised, or was abandoned.

Verified directly: `break`-ing out of iteration early and checking the log confirmed the generator-aware wrapper correctly reported an incomplete run rather than falsely claiming success.

### 9. A follow-up bug caused by an incomplete fix
While applying the fix for #8, moved the line marking success (`status = "successful!"`) to *before* the loop instead of after it. This meant it was already marked "successful" before any iteration happened at all, making the log lie about early-abandonment even after the `finally` fix. Confirmed and corrected by re-running the exact same `break` test and checking the log actually changed. A reminder that line *placement* relative to a loop or yield point is not cosmetic — it changes correctness.

### 10. Context manager not cleaning up if writeback failed
The custom `FM_for_KV_store.__exit__` originally ran `write_back()` and `self.file.close()` back to back with no protection — if `write_back` raised, the file handle would leak (never closed). Fixed with `try: write_back(...) finally: self.file.close()`, guaranteeing cleanup regardless of outcome — the same `finally` principle from bug #8/#9, applied to file handles instead of generator state.

### 11. Known, accepted limitation: exception masking in `__exit__`
If an operation inside the `with` block raises (e.g. `KeyError` from a bad delete) **and** `write_back` inside `__exit__` also raises, Python's exception chaining means the *second* exception becomes the one that actually propagates — the original gets attached as context but is no longer the "active" error. Deliberately left unfixed: the probability of both failures co-occurring is low and the consequence (a confusing traceback, not silent data loss) is minor for a small project. Noted here as a known tradeoff, not an oversight — the underlying judgment (probability × consequence, not "small project = don't fix anything") is the actual lesson.

## Design notes worth remembering

- `data` (in-memory dict) is the source of truth during a run; the file is the persistence layer. `list_all()` reads from `data`, not the file, so it reflects the current session's state including uncommitted changes.
- Every operation is atomic enough that a crash mid-operation never leaves `data` in a half-mutated state — which is precisely what makes it safe for `__exit__` to always write back on the way out, even after a failure.
