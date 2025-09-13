# ModelGuard

# Trustworthy Model Re-Use — Phase 1 (CLI)

Minimal scaffold for a CLI that:
- reads a newline-delimited file of URLs, and
- prints one NDJSON record per **model** URL (placeholder values for now).

We’ll fill in real metrics and details once parts are working.

---

## Quickstart

```bash
# (optional) create & activate a venv
python3 -m venv venv && source venv/bin/activate

# make the entrypoint executable (one time)
chmod +x run

# install tools/deps
./run install
```


## Project layout (initial)

```
.
├─ run                  # entrypoint (install | test | URL_FILE)
├─ README.md
├─ requirements.txt     # minimal for now
├─ .gitignore
├─ .github/workflows/   # (optional) CI later
├─ src/
│   ├─ metrics/         # metric modules (placeholders now)
│   │   └─ 
│   └─ main.py
│     
└─ tests/
   └─ test_cli.py      # basic tests (add more over time)
```

## Notes

- **Stdout** is reserved for NDJSON output when processing URLs.
- Set `LOG_FILE` and `LOG_LEVEL` if you want logs during development:
  ```bash
  export LOG_FILE="$(pwd)/tmr.log"
  export LOG_LEVEL=1   # 0=silent, 1=info, 2=debug
  ```
- We’ll document metric definitions, weighting, and CI details once those parts are implemented.