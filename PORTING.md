# Porting QGIS plugins to QGIS 4

QGIS 4 runs on Qt 6. A QGIS 4-only port should remove Qt 5/QGIS 3 compatibility code instead of carrying fallback imports and event adapters indefinitely.

## Metadata

- Set `qgisMinimumVersion=4.0`.
- Set `qgisMaximumVersion=4.99`.
- Do not add `supportsQt6=True`; QGIS no longer recognizes it for repository compatibility.

## Imports

- Use the QGIS Qt shim, `qgis.PyQt`, instead of direct `PyQt6` imports.
- Update moved Qt classes to their Qt 6 modules. A common example is `QAction`, which now belongs in `QtGui`:

```python
from qgis.PyQt.QtGui import QAction
```

## Enums

Use scoped enum names required by Qt 6 and QGIS 4.

Examples:

- `Qt.ArrowCursor` -> `Qt.CursorShape.ArrowCursor`
- `Qt.UserRole` -> `Qt.ItemDataRole.UserRole`
- `Qgis.Warning` -> `Qgis.MessageLevel.Warning`
- `QgsMapLayer.VectorLayer` -> `QgsMapLayer.LayerType.VectorLayer`
- `QgsWkbTypes.PolygonGeometry` -> `QgsWkbTypes.GeometryType.PolygonGeometry`
- APIs that group geometry families may now use `Qgis.GeometryType`, for example `Qgis.GeometryType.Point`, `Qgis.GeometryType.Line`, and `Qgis.GeometryType.Polygon` in `QgsRubberBand`, `QgsGeometry.type()`, and `QgsVectorLayer.geometryType()`.

## Field types

Use `QMetaType.Type` values when creating `QgsField` objects.

Example:

```python
from qgis.PyQt.QtCore import QMetaType

QgsField("name", QMetaType.Type.QString)
```

This replaces old `QVariant.String` style type values.

## Events and dialogs

- Replace Qt 5 mouse position APIs with Qt 6 APIs: use `position()` instead of `pos()` and `globalPosition()` instead of `globalPos()`.
- Convert `QPointF` positions with `toPoint()` when passing integer pixel positions to QGIS APIs.
- Prefer `exec()` over the old `exec_()` compatibility alias for dialogs and menus.

## Mechanical checks

- Search for direct Qt imports: `rg "PyQt5|PyQt6"`.
- Search for compatibility fallbacks that can be removed: `rg "ImportError|hasattr\\(|globalPos\\(|\\.pos\\(|exec_\\("`.
- Search for unscoped Qt and QGIS enums: `rg "Qt\\.[A-Z]|Qgis\\.[A-Z]|QgsMapLayer\\.[A-Z]|QgsWkbTypes\\.[A-Z]"`.
- Run the QGIS migration helper or Docker checker where possible, then manually review the diff.

## Validation

- Start QGIS 4 with the plugin enabled and confirm it loads without import errors.
- Exercise every action, map tool, signal, dialog, and settings path.
- Check packaging metadata before upload so the plugin appears in the QGIS 4-compatible repository listings.

## References

- https://plugins.qgis.org/docs/migrate-qgis4
- https://github.com/qgis/QGIS/wiki/Plugin-migration-to-be-compatible-with-Qt5-and-Qt6
