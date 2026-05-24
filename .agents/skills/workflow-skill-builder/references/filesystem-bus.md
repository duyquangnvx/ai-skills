# Filesystem as Message Bus

The orchestrator does not collect agent results from `Task` return values. Agents write results to disk, and the orchestrator polls files. This keeps the orchestrator's context bounded.

## Convention

For each agent task:

- **Success:** `<output-dir>/<identifier>.json` — contains the result payload
- **Failure:** `<output-dir>/<identifier>.error` — contains the error message

`<identifier>` uniquely identifies the agent's input (source name, item id, date + run number).

Example layout:

```
data/
├── scans/
│   ├── source-a/2026-05-24-run1.json
│   ├── source-b/2026-05-24-run1.json
│   └── source-c/2026-05-24-run1.error
└── classifications/
    ├── item-001.json
    ├── item-002.json
    └── item-003.error
```

## Poll loop pattern

After spawning a fan-out batch, the orchestrator polls:

```bash
EXPECTED=18
TIMEOUT=600
ELAPSED=0
START=$(date +%s)

while [ $ELAPSED -lt $TIMEOUT ]; do
  SUCCESS=$(ls -1 data/scans/*/${TODAY}-run*.json 2>/dev/null | wc -l)
  ERRORS=$(ls -1 data/scans/*/${TODAY}-run*.error 2>/dev/null | wc -l)
  TOTAL=$((SUCCESS + ERRORS))
  if [ "$TOTAL" -ge "$EXPECTED" ]; then break; fi
  sleep 10
  ELAPSED=$(( $(date +%s) - START ))
done

echo "Phase complete: $SUCCESS ok, $ERRORS failed (expected $EXPECTED)"
```

The orchestrator does NOT parse output payloads here — it only counts files. It moves to the next phase as soon as `(success + error) >= expected` OR the wall-clock timeout fires.

## Atomic writes

Agents must write to a temp file and rename, to avoid the orchestrator reading a half-written file:

```bash
echo "$RESULT" > "$OUTPUT_PATH.tmp"
mv "$OUTPUT_PATH.tmp" "$OUTPUT_PATH"
```

Document this in every agent definition that writes results.

## Why filename-only polling

The orchestrator's context grows by `O(n × filename_length)` not `O(n × output_size)`. With 18 sources producing 10 KB results each, naive collection adds ~180 KB to the orchestrator's context per phase; filename polling adds ~1 KB.

The next phase that actually needs the payloads reads only the files it processes — typically one at a time, possibly inside a sub-fan-out.

## Identifier conventions

Pick identifiers that are:

- **Stable across reruns** so reruns overwrite rather than duplicate
- **Greppable** for status checks (`ls data/scans/*/run1.json | wc -l`)
- **Sortable** for chronological audits

Common patterns:

| Pattern | When |
|---|---|
| `<source>/<YYYY-MM-DD>-run<N>.json` | Daily batched jobs |
| `<source>/<item-id>.json` | Per-item processing where items have stable ids |
| `<phase>/<input-hash>.json` | Content-addressable for caching |

Pick one pattern per phase and stick with it. Mixing patterns within a phase makes the poll glob impossible to write cleanly.

## Cross-phase reads

A later phase reads the previous phase's outputs by globbing the success directory:

```bash
for f in data/scans/*/run1.json; do
  process "$f"
done
```

If a phase needs to know which items failed in the previous phase, it globs the `.error` files. This keeps each phase loosely coupled — they share only the directory layout.
