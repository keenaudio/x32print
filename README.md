# x32print

Generate printable documentation from Behringer X32 scene files.

**Status: early development scaffold (0.1.0).** This package is designed as the foundation for the project, not yet a fully validated X32 scene parser. It includes a working CLI, demo report, data model, HTML report, validation framework, and a conservative first-pass parser. Input routing interpretation still needs to be verified against real `.scn` files.

## Requirements

- macOS, Windows, or Linux
- Python 3.12+
- VS Code (optional)
- Internet access for the initial dependency installation

Check your Python version:

```bash
python3 --version
```

## Open and run on macOS

1. Unzip the downloaded archive.
2. Open the `x32print` folder in VS Code (`File → Open Folder…`).
3. In VS Code, open **Terminal → New Terminal**.
4. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. Install the package and development tools:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"
   ```

6. Generate a sample report:

   ```bash
   x32print --demo
   ```

   This creates `x32print-demo.html` in the current directory. Open it in Safari or Chrome and use the Print button or the browser's Print command to save a PDF.

## Using an X32 scene file

```bash
x32print path/to/your-scene.scn
```

The command writes an HTML report beside the scene file, using the same base filename. You can choose an explicit output path:

```bash
x32print path/to/your-scene.scn --output my-report.html
```

The initial parser reads the text-based scene directives and extracts a limited set of channel labels, scribble-strip colors, and bus names. **It does not yet decode `/config/routing/IN` into verified Local/AES50/Card/Aux source assignments.** Until that is implemented and tested against real scene fixtures, the source column is marked as unresolved rather than guessing. The report also includes validation warnings where applicable.

## Development

Run tests:

```bash
pytest
```

Run the CLI without installing the console script:

```bash
python -m x32print --demo
```

## Architecture

```text
Scene file
   ↓
Parser (raw directives + conservative extraction)
   ↓
Scene data model
   ↓
Routing interpreter / validators
   ↓
Report registry
   ↓
HTML report
```

Key design rules:

- The parser does not render reports.
- Reports consume model objects, not scene-file syntax.
- Routing interpretation is separate from parsing.
- Unknown directives are retained in `Scene.raw_directives`.
- Unknown routing formats must not be silently mapped to invented sources.

## Project layout

```text
src/x32print/
  __init__.py
  __main__.py
  cli.py
  parser.py
  routing.py
  validator.py
  colors.py
  config.py
  models.py
  reports/
    __init__.py
    base.py
    html.py
  templates/
    report.html.j2
    report.css
tests/
  test_parser.py
  test_routing.py
  test_validator.py
```

## Current scope and next milestone

- [x] Package structure and installable CLI
- [x] Data models and raw directive preservation
- [x] Demo HTML report
- [x] Input, stage-box placeholder, bus, and validation report sections
- [x] Basic automated tests
- [ ] Validate scene syntax against representative `.scn` files
- [ ] Decode `/config/routing/IN` without fixed AES50 assumptions
- [ ] Derive stage-box groupings from decoded source objects
- [ ] Add output routing and further report types

## License

MIT. See [LICENSE](LICENSE).
