# x32print — Design Philosophy, Goals, and Product Direction

**Status:** Working design brief  
**Purpose:** Capture the product decisions and development principles agreed during initial planning.  
**Audience:** Maintainers, contributors, and future coding assistants.

## 1. Product vision

**x32print** is an open-source Python utility that converts Behringer X32 scene (`.scn`) files into accurate, professional, easy-to-print documentation for live-sound workflows.

The goal is not merely to dump scene settings. It is to produce useful operational documents that a sound engineer, stagehand, musician, volunteer, or technician can understand at a glance—especially under show conditions.

The initial emphasis is on input lists, physical stage-box patches, monitor buses, and a concise stage patch sheet. Over time, the same foundation should support more comprehensive console documentation and scene comparison.

## 2. Intended users and use cases

- Live sound engineers preparing or documenting a show.
- Bands and touring crews coordinating stage inputs and monitors.
- Churches and volunteer production teams needing clear handoff documents.
- Theaters, schools, and other venues with repeatable show configurations.
- Technicians diagnosing a mismatch between physical cabling and mixer routing.

A successful report should help answer practical questions such as:

- What is plugged into stage-box input 12?
- Which X32 mixer channel receives that input?
- What is the channel called on the console?
- Which buses are being used as monitor mixes?
- Is there a potentially confusing label or patch conflict?

## 3. Guiding principles

### Accuracy before appearance

Never infer a physical patch from channel position alone. A polished but incorrect stage-box sheet is worse than an incomplete one. If routing cannot be decoded reliably, show it as unresolved and explain the limitation.

### Parse once, render many ways

Scene parsing, routing interpretation, validation, and report presentation should be separate responsibilities. The same structured scene representation should serve HTML, plain text, CSV, JSON, and future output formats.

### Print-first, screen-friendly

HTML is the primary presentation format because it supports real color swatches, strong typography, responsive layout, and browser printing to PDF. Printed pages must remain legible and useful, including when printed in grayscale.

### Useful to nonexperts

Prefer clear terms and physical patch references over opaque console tokens. Show mixer channel numbers where relevant, but omit them from a stage-only patch sheet intended for people plugging in cables.

### Conservative interpretation

Support unknown or newly introduced scene directives without crashing. Preserve raw information where practical; do not silently guess meanings for unsupported routing, colors, or icons.

### Incremental, testable development

Deliver small, verifiable capabilities using real `.scn` fixtures. A narrow feature that is correct and tested is preferable to a broad feature that assumes the routing semantics.

### Open-source maintainability

Use readable modern Python, clear module boundaries, typed models, tests, documentation, and a contributor-friendly repository. Favor the standard library unless a dependency materially improves the result.

## 4. Input and output strategy

**Input:** Behringer X32 `.scn` scene files. The first development fixture may be `JasonNeverBetter.scn`, but the implementation must be generic and must not hardcode one show's labels, equipment, or patch layout.

**Primary output:** A standalone HTML report with embedded or reliably packaged styling, suitable for viewing in a browser and printing or saving as PDF.

**Original version-one output goal:** Both `scene.html` and `scene.txt`. The current starter scaffold generates HTML only; plain-text output remains to be implemented.

**Later outputs:** CSV, JSON, Excel, and potentially direct PDF generation. Export formats should consume the same interpreted scene data, not duplicate parsing logic.

## 5. Proposed architecture

```text
X32 .scn file
    |
    v
Raw scene parser
    |
    v
Structured Scene model
    |
    v
Routing / semantic interpreter
    |
    +----> Validation framework
    |
    v
Report registry and report plugins
    |
    +----> HTML renderer / themes
    +----> Text renderer
    +----> Future CSV / JSON / PDF renderers
    |
    v
CLI and generated artifacts
```

### 5.1 Raw parser

Read scene directives and extract their literal values without making unwarranted assumptions about physical routing. Handle blank lines, comments, unfamiliar directives, and partial scenes gracefully. Retain raw directives when practical for future interpretation and debugging.

### 5.2 Scene data model

Use Python dataclasses and type hints. The initial model should include:

- **Scene:** name/metadata, channels, buses, routing information, and preserved raw directives.
- **Channel:** mixer channel number, label, input source, source device/port where known, scribble-strip color, icon, and optional notes.
- **Bus:** bus number, label, scribble-strip color, icon, and optional notes.
- **RoutingMap:** actual configured routing blocks and interpreted input assignments.
- **InputSource:** structured source identity (such as source family, device, port, and channel number), not just a preformatted display string.

The model should be extensible to outputs, aux inputs, matrices, DCAs, mute groups, FX, and snippets without forcing all of them into version one.

### 5.3 Interpreter and routing decoder

A dedicated interpreter translates scene-level tokens into meaningful signal paths. Keep routing decoding in focused functions/modules, for example:

- `decode_input_routing(...)`
- `decode_output_routing(...)` (future)
- `group_stageboxes(...)`

**Critical requirement:** Do not assume mixer channels 1–16 originate from AES50-A and 17–32 from AES50-B. Read the actual `/config/routing/IN` configuration and resolve source blocks accordingly. Design for Local, AES50-A, AES50-B, Card, Aux, and additional options as they are confirmed.

The physical input number, stage-box/device identity, and destination mixer channel are distinct concepts. Reports must preserve those distinctions.

### 5.4 Validation framework

Implement validators as independent checks that can be registered and extended. Initial candidates:

- Duplicate channel labels.
- Blank channel labels.
- Duplicate physical source assignments or routing conflicts, where semantics are known.
- Blank bus names.
- Unused routed inputs, where enough information exists to establish them.

Warnings should be clearly visible but not prevent generating otherwise useful reports. A check that cannot yet be performed must be marked **unavailable/not implemented**, not reported as passed.

### 5.5 Report plugins and registry

Reports should be independent of parsing and assembled through a registry. Planned report classes include:

- `InputReport`
- `StageBoxReport`
- `BusReport`
- `ValidationReport`

This allows the CLI and future configuration to select report sections without modifying the core parser. External plugin support is a possible future extension, not a requirement for the first release.

### 5.6 Themes and configuration

Separate visual design from report content. Initial/default styling should be restrained and print-oriented; future theme choices may include `default`, `compact`, `large-print`, and `dark`.

A future YAML or similar configuration file may control enabled reports, theme, paper size, orientation, notes-column width, and related presentation settings.

## 6. Version-one reports

### 6.1 Input Channels

A readable table with:

1. Mixer channel number.
2. Resolved input source.
3. Channel label/name.
4. Scribble-strip color **swatch**, placed after the label and before notes.
5. A generously sized notes area, blank by default for handwriting.

The report should not substitute abbreviations for actual color swatches. If a color code is unknown, indicate that honestly rather than assigning an invented color.

### 6.2 Stage Box reports

Automatically group physical inputs by the **actual decoded routing** and source device, not by fixed mixer-channel ranges. For each physical input, show its port number, connected channel/label, and other useful patch details.

The initial user's system includes two S16 stage boxes, often thought of as Stage Box A (1–16) and B (17–32), but that setup is a test case—not a universal routing rule.

### 6.3 Monitor Busses

Document bus number, bus name, and a broad notes column. Focus on monitor/mix buses. Do **not** include matrices, DCAs, or FX returns in this report.

### 6.4 One-page Stage Patch Summary

Create a condensed sheet for stage crews. Prioritize **physical stage input number + source label** and stage-box grouping. Do not show mixer channel numbers on this stage-facing summary. Aim to fit on one printed page where practical.

### 6.5 Validation Summary

Present actionable warnings separately and clearly, with enough context to locate the affected channel, bus, or patch. Avoid implying that incomplete validation proves a scene is correct.

## 7. HTML and print design philosophy

The result should feel like carefully typeset technical documentation, not an unformatted spreadsheet export.

- Clear title, scene identity, and section hierarchy.
- Restrained palette; real scribble-strip swatches for fast recognition.
- Spacious tables, alternating row treatment, minimal visual clutter.
- Notes column wider than routine metadata columns.
- Landscape orientation when it materially improves table legibility.
- Sensible page breaks and repeating table headers when printed.
- No important data cut off at page boundaries.
- A **Print** button visible on screen but hidden in print CSS.
- A footer identifying `x32print`, version, generation date, scene name, and optionally the GitHub project URL.
- Responsive browser presentation without compromising the printed layout.

The existing `BadCat_StagePlan.html` prototype is a **visual reference** for sections, swatches, and print workflow. It is not a source of truth for routing semantics or parser behavior.

## 8. Command-line experience

The simplest path should work without a configuration file:

```bash
x32print show.scn
```

The original target is to generate `show.html` and `show.txt` alongside the scene. The starter currently generates only HTML.

Additional options can grow incrementally:

```bash
x32print show.scn --html
x32print show.scn --csv
x32print show.scn --config config.yml
```

A `--demo` option is useful for quickly viewing report styling before real routing support is complete. CLI errors should be concise, specific, and actionable.

## 9. Quality, compatibility, and testing

- Target **Python 3.12+** with type hints and dataclasses.
- Keep functions small, cohesive, and straightforward to test.
- Avoid unnecessary global state.
- Use real scene fixtures to verify parsing and routing behavior.
- Add unit tests for parsing, routing interpretation, validators, and report generation.
- Test nondefault routing and partial/unknown directives explicitly.
- Confirm numeric scribble-strip color and icon mappings against reliable fixtures or documentation before presenting them as authoritative.
- Use GitHub Actions for automated test runs.
- Favor deterministic output, with explicitly identified generated metadata such as timestamps.

## 10. Repository and contributor experience

The project should be suitable for public GitHub hosting and eventual PyPI distribution. Include:

- `pyproject.toml` and an installable console entry point.
- Clear `README.md` with overview, installation, usage, screenshots/examples, roadmap, and contribution instructions.
- `LICENSE`, `CONTRIBUTING.md`, and changelog.
- Sample scenes where redistribution is appropriate, plus expected report output.
- Tests and CI.
- A modular `src/x32print/` package layout.

Development should work comfortably in VS Code on macOS using a virtual environment and editable installation.

## 11. Future roadmap

Potential expansions, in no strict priority order:

- Plain text, CSV, JSON, Excel, and direct PDF exports.
- Output routing and physical output patch reports.
- Aux input, matrix, DCA, FX, mute group, and snippet reports.
- Phantom power, preamp gain, channel configuration, and other technical detail.
- Console icon support and a color legend.
- Scene-to-scene diff and change reports.
- Customizable report themes and configuration.
- More complete routing coverage across X32 firmware/scene variants.
- **Rack & Stage Wiring Report:** a human-readable physical signal-path overview, such as `S16 input → AES50 link → X32 input block → mixer channel`, useful for setup and troubleshooting.
- Optional third-party report plugins.

## 12. Development sequence

1. Establish the installable package, CLI, test setup, and report shell.
2. Obtain representative real `.scn` files and document the directives they contain.
3. Confirm parser behavior and numeric mappings using those fixtures.
4. Implement and test real input-routing interpretation.
5. Populate the physical stage-box and patch-summary reports from verified routing.
6. Implement validation checks with explicit support status.
7. Refine print styling and test browser/PDF output.
8. Add the original plain-text output target.
9. Expand supported scene features and output formats incrementally.

## 13. Current starter scaffold: scope and limitations

The initial downloadable `x32print-starter.zip` is a **development scaffold**, not a complete X32 scene interpreter. It includes a Python package, basic CLI, provisional scene parser/models, routing module, validator, HTML/Jinja2 template and CSS, sample/demo report, tests, and repository documentation.

At this stage:

- HTML report generation and `x32print --demo` are the immediate demonstration paths.
- The parser extracts selected channel/bus directives and captures routing tokens.
- Routing semantics are **not yet decoded**, so physical patch assignments and stage-box grouping must not be claimed as verified.
- Color mappings remain provisional pending confirmation.
- Plain-text export, a full report registry, complete stage-box reports, and broader validation are not yet finished.

The next high-value development step is to test against a real scene file, especially its `/config/routing/IN` lines, before implementing authoritative stage-box documentation.

## 14. Definition of success

A sound engineer should be able to run one command against an X32 scene and receive a clean report that accurately reflects the configured signal path. A stage crew should be able to use the patch summary without needing to understand mixer channel routing. A maintainer should be able to add a new report or export format without rewriting the parser. Above all, the utility should distinguish **known**, **unknown**, and **unsupported** information reliably.

---

*This document records the initial design discussion and should evolve as real X32 scene fixtures, routing behavior, and user feedback establish new requirements.*
