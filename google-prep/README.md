# Google Coding Prep Notebook

A single-page, Python-first study guide for Google coding interviews:
24 patterns explained in plain English, a template for each, and 123 easy,
medium and hard problems with worked solutions.

- `google-interview-guide.html` – the generated page (open it in a browser).
- `build.py` – runs every code block in the guide as a test, then writes the HTML.
- `content/` – the guide's text and code, one module per group of patterns.

Rebuild after editing content:

```bash
python3 build.py            # fails if any solution's asserts fail
python3 build.py --no-test  # skip running the code blocks
```
