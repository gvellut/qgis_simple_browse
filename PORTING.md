# Porting QGIS plugins to QGIS 4

QGIS 4 runs on Qt 6, so most plugin changes are Qt/PyQt compatibility updates plus plugin metadata. Prefer changes that keep one source tree working on both QGIS 3 and QGIS 4 unless you have a reason to drop QGIS 3 support.

## Metadata

- If the plugin should support QGIS 3 and QGIS 4, keep the current `qgisMinimumVersion` and add `qgisMaximumVersion=4.99`.
- If the plugin should support only QGIS 4, set `qgisMinimumVersion=4.0` and omit `qgisMaximumVersion`.
- Do not add `supportsQt6=True`; QGIS no longer recognizes it for repository compatibility.

## Imports

- Use the QGIS compatibility shim, not direct `PyQt5` or `PyQt6` imports: `qgis.PyQt`.
- Check Qt modules that moved in Qt 6. A common example is `QAction`, which moved from `QtWidgets` to `QtGui`.
- For cross-version code, import from the Qt 6 location first and fall back to the Qt 5 location if needed.

## Enums

Use scoped enum names. They work with Qt 6 and are generally compatible with recent QGIS 3/PyQt 5 builds.

Examples:

- `Qt.ArrowCursor` -> `Qt.CursorShape.ArrowCursor`
- `Qt.UserRole` -> `Qt.ItemDataRole.UserRole`
- `Qgis.Warning` -> `Qgis.MessageLevel.Warning`
- `QgsMapLayer.VectorLayer` -> `QgsMapLayer.LayerType.VectorLayer`
- `QgsWkbTypes.PolygonGeometry` -> `QgsWkbTypes.GeometryType.PolygonGeometry`

## Events and dialogs

- Mouse and wheel event APIs changed in Qt 6. Prefer helpers that use `position()` / `globalPosition()` when available and fall back to `pos()` / `globalPos()` for Qt 5.
- `exec_()` compatibility aliases may disappear in Qt 6 bindings. Prefer `exec()` for Qt dialogs and menus.
- When passing positions to QGIS APIs that expect integer pixel `QPoint`s, convert Qt 6 `QPointF` values with `toPoint()`.

## Mechanical checks

- Search for direct Qt imports: `rg "PyQt5|PyQt6"`.
- Search for unscoped Qt and QGIS enums: `rg "Qt\\.[A-Z]|Qgis\\.[A-Z]|QgsMapLayer\\.[A-Z]|QgsWkbTypes\\.[A-Z]"`.
- Search for Qt 5 event/dialog APIs: `rg "globalPos\\(|\\.pos\\(|exec_\\("`.
- Run the QGIS migration helper or Docker checker where possible, then manually review the diff.

## Validation

- Start QGIS 4 with the plugin enabled and confirm it loads without import errors.
- Exercise every tool action and dialog path; static checks do not prove PyQGIS runtime compatibility.
- If maintaining QGIS 3 support, repeat the same smoke test in the oldest QGIS 3 version declared by `qgisMinimumVersion`.

## References

- https://plugins.qgis.org/docs/migrate-qgis4
- https://github.com/qgis/QGIS/wiki/Plugin-migration-to-be-compatible-with-Qt5-and-Qt6
