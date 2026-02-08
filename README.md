# Simple Browse (QGIS plugin)

Single “Google Maps”-like interaction tool:

- Click (no drag): delegates to QGIS Identify Features behavior (using the current Identify settings)
- Drag: pans like Pan Map
- Mouse wheel: zoom in/out (pointer-focused)
- Double click: zoom in (pointer-focused)

The plugin keeps *Simple Browse* active while delegating click/drag handling to QGIS’ built-in Identify/Pan tools (they won’t appear as the active tool).

## Install (development)

1. Set the env var QGIS_PLUGINPATH to the directory eg `/Users/guilhem/Documents/projects/github/qgis_simple_browse`
2. Restart QGIS.
3. Enable the plugin in **Plugins → Manage and Install Plugins…**.
4. (optional) For development, install the **Plugin Reloader** plugin 

*Note*: Multiple plugin paths can be passed, separated with `:`
