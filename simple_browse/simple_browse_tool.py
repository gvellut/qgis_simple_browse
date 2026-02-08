from __future__ import annotations

import logging

from qgis.core import Qgis, QgsMessageLog
from qgis.gui import (
    QgsAttributeDialog,
    QgsIdentifyMenu,
    QgsMapTool,
    QgsMapToolIdentify,
    QgsMapToolPan,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication

logger = logging.getLogger(__name__)


def log_info(msg: str, level=Qgis.Info):
    QgsMessageLog.logMessage(
        msg,  # The message
        "Simple Browse",  # The "Tag" (this becomes the Tab name)
        level=level,  # The severity level
    )


class SimpleBrowseMapTool(QgsMapTool):
    """Single tool: click identifies, drag pans, wheel/double-click zooms."""

    def __init__(self, iface, action):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        super().__init__(self.canvas)

        self.setAction(action)

        self._pan_tool = QgsMapToolPan(self.canvas)
        self._identify_tool = QgsMapToolIdentify(self.canvas)
        self.menu = QgsIdentifyMenu(self.canvas)
        self.menu.setAllowMultipleReturn(False)
        self.menu.setExecWithSingleResult(False)

        self._press_event = None
        self._press_pos = None
        self._is_panning = False

        self._drag_threshold = max(3, QApplication.startDragDistance())

    def activate(self):
        super().activate()
        self.canvas.setCursor(Qt.ArrowCursor)
        self._reset_state()

    def deactivate(self):
        self._reset_state()
        self.canvas.setCursor(Qt.ArrowCursor)
        super().deactivate()

    def _reset_state(self):
        self._press_event = None
        self._press_pos = None
        self._is_panning = False

    def canvasPressEvent(self, event):
        self._press_event = event
        self._press_pos = event.pos()
        self._is_panning = False
        self.canvas.setCursor(Qt.ArrowCursor)

    def canvasMoveEvent(self, event):
        if self._press_pos is None:
            return

        if not self._is_panning:
            if (
                event.pos() - self._press_pos
            ).manhattanLength() >= self._drag_threshold:
                self._start_pan(event)

        if self._is_panning:
            try:
                self._pan_tool.canvasMoveEvent(event)
            except Exception:
                # keep our tool stable even if delegation fails
                pass

    def _start_pan(self, event):
        self._is_panning = True
        self.canvas.setCursor(Qt.ClosedHandCursor)

        # Pan tool expects a press before move.
        try:
            if self._press_event is not None:
                self._pan_tool.canvasPressEvent(self._press_event)
        except Exception:
            pass

        try:
            self._pan_tool.canvasMoveEvent(event)
        except Exception:
            pass

    def canvasReleaseEvent(self, event):
        if self._is_panning:
            try:
                self._pan_tool.canvasReleaseEvent(event)
            except Exception:
                pass

            self.canvas.setCursor(Qt.ArrowCursor)
            self._reset_state()
            return

        # Click without drag -> Identify.
        self._do_identify(event)
        self._reset_state()

    def _do_identify(self, release_event):
        if self._identify_tool is not None:
            try:
                # Use the identify() method to get results
                results = self._identify_tool.identify(
                    release_event.x(),
                    release_event.y(),
                )

                if len(results) == 1:
                    # Show the identify results dialog
                    self.close_feature_form()
                    self.iface.openFeatureForm(results[0].mLayer, results[0].mFeature)
                else:
                    # Case B: Multiple features -> Show the Identify Menu
                    # This pops up the QGIS list widget at the mouse cursor
                    for res in results:
                        if res.mLayer:
                            # TODO change with name : add name to KML or output layer

                            # this changes the Display > Display name in layer
                            # so not just for this interaction
                            # instead of setting here : set the display name
                            # in layer when creating the QGS
                            res.mLayer.setDisplayExpression('"id"')

                    point = release_event.globalPos()
                    selected_results = self.menu.exec(results, point)

                    # The menu returns a list of selected results (usually just one)
                    if selected_results:
                        self.close_feature_form()
                        self.iface.openFeatureForm(
                            selected_results[0].mLayer, selected_results[0].mFeature
                        )
                return
            except Exception as e:
                log_info(f"Identify error: {e}", Qgis.Warning)

    def close_feature_form(self):
        """Closes all open QgsAttributeDialog instances."""
        for widget in QApplication.allWidgets():
            if widget.metaObject().className() == "QgsAttributeDialog" or isinstance(
                widget, QgsAttributeDialog
            ):
                log_info(f"Closing existing form: {widget.windowTitle()}")
                widget.close()

    def canvasDoubleClickEvent(self, event):
        # Double-click zoom in (same feel as one wheel step).
        # Keep the point under the mouse cursor in the same location after zoom.
        try:
            # Get the map point under the cursor
            transform = self.canvas.getCoordinateTransform()
            center_point = transform.toMapCoordinates(event.pos())

            # Zoom in
            self.canvas.zoomIn()

            # Recenter on the original point under the cursor
            self.canvas.setCenter(center_point)
            self.canvas.refresh()
        except Exception:
            pass

    def wheelEvent(self, event):
        # Enable wheel zoom while tool is active.
        try:
            delta_y = event.angleDelta().y()
        except Exception:
            delta_y = 0

        if delta_y == 0:
            return

        steps = int(delta_y / 120) if delta_y % 120 == 0 else (1 if delta_y > 0 else -1)

        try:
            if steps > 0:
                for _ in range(abs(steps)):
                    self.canvas.zoomIn()
            else:
                for _ in range(abs(steps)):
                    self.canvas.zoomOut()
        except Exception:
            pass
