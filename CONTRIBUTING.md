# Contributing

This is a design-note repository first. Contributions that sharpen the
architecture, the measurement protocol, or the evidence are more useful than
additional slogans.

## Good contributions

- A counterexample where the promotion gate would fail.
- A reproducible measurement protocol for one metric (e.g. phase margin).
- A public-data experiment on an open PDK.
- A correction with a citation.
- A diagram improvement that keeps the figure editable.

## Rules

1. **No proprietary data.** Do not paste commercial PDK models, NDA netlists,
   or foundry extraction tables.
2. **Separate fact from hypothesis.** Mark estimates and proposals as such.
3. **Cite sources.** Preprints are fine; label them as preprints.
4. **Do not claim silicon validation** unless you have it.
5. **Keep diagrams generated.** Edit `scripts/build_diagrams.py`, not only the SVG.
   CI checks SVG determinism; PNG bytes may vary with the local cairo build.

## Local checks

```bash
python3 -m venv .venv
.venv/bin/pip install cairosvg pyyaml jsonschema
.venv/bin/python scripts/build_diagrams.py
.venv/bin/python scripts/validate.py
```

## Discuss

Open a Discussion for architecture questions; use Issues for broken links,
schema errors, or factual corrections.
