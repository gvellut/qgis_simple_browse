# Simple Browse (QGIS plugin)

Single “Google Maps”-like interaction tool:

- Click (no drag): delegates to QGIS Identify Features behavior (using the current Identify settings)
- Drag: pans like Pan Map
- Mouse wheel: zoom in/out
- Double click: zoom in

## Install (development)

1. Copy the folder `simple_browse/` into your QGIS profile plugins folder:

	- macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

2. Restart QGIS.
3. Enable the plugin in **Plugins → Manage and Install Plugins…**.

## Notes

The plugin keeps *Simple Browse* active while delegating click/drag handling to QGIS’ built-in Identify/Pan tools (they won’t appear as the active tool).