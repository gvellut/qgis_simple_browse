# Simple Browse (QGIS plugin)

Single “Google Maps”-like interaction tool:

- Click (no drag): delegates to QGIS Identify Features behavior (using the current Identify settings)
- Drag: pans like Pan Map
- Mouse wheel: zoom in/out (pointer-focused)
- Double click: zoom in (pointer-focused)

The plugin keeps *Simple Browse* active while delegating click/drag handling to QGIS’ built-in Identify/Pan tools (they won’t appear as the active tool).


## lint

Run those comments and fix the issues before finishing a session.

```bash
# Run linting and formatting. Always use --fix.
ruff check --fix
ruff format
```