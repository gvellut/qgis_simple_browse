from __future__ import annotations

import logging

from qgis.core import Qgis, QgsMessageLog, QgsRectangle
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
        # 1. Define the Zoom Factor (1.5x magnification)
        # We divide the extent size by this factor to zoom in.
        factor = 1.5

        # 2. Get current canvas, extent, and dimensions
        canvas = self.canvas
        current_extent = canvas.extent()
        canvas_width = canvas.width()
        canvas_height = canvas.height()

        # 3. Get mouse position in Pixels and Map Coordinates
        screen_pos = event.pos()
        # Convert pixels (QPoint) to map coordinates (QgsPointXY)
        map_point = canvas.getCoordinateTransform().toMapCoordinates(screen_pos)

        # 4. Calculate the new extent size (Smaller area = Zoom In)
        new_width = current_extent.width() / factor
        new_height = current_extent.height() / factor

        # 5. Calculate the relative position of the mouse on the screen (0.0 to 1.0)
        ratio_x = screen_pos.x() / canvas_width
        ratio_y = screen_pos.y() / canvas_height

        # 6. Calculate the new Extent coordinates
        # We shift the new extent so that 'map_point' remains at the same screen ratio
        new_xmin = map_point.x() - (new_width * ratio_x)
        new_xmax = new_xmin + new_width

        # Note: Screen Y starts at Top (0), Map Y usually starts at Bottom (Min)
        # We calculate from the Top (YMax) down.
        new_ymax = map_point.y() + (new_height * ratio_y)
        new_ymin = new_ymax - new_height

        # 7. Apply the new extent
        new_extent = QgsRectangle(new_xmin, new_ymin, new_xmax, new_ymax)
        canvas.setExtent(new_extent)
        canvas.refresh()

    def wheelEvent(self, event):
        # 1. Get Wheel Delta
        try:
            delta_y = event.angleDelta().y()
        except Exception:
            delta_y = 0

        if delta_y == 0:
            return

        # 2. Define Base Zoom Factor
        # 1.25 is a standard "smooth" step.
        # If scaling multiple steps at once, we use power logic.
        zoom_base = 1.25

        # Calculate how many "clicks" occurred (usually 120 per click)
        steps = delta_y / 120

        # Calculate the total scale factor.
        # Positive steps (Zoom In) -> factor > 1
        # Negative steps (Zoom Out) -> factor < 1 (e.g. 0.8)
        if steps > 0:
            factor = zoom_base**steps
        else:
            factor = 1.0 / (zoom_base ** abs(steps))

        # 3. Get Canvas and Dimensions
        canvas = self.canvas
        current_extent = canvas.extent()
        canvas_width = canvas.width()
        canvas_height = canvas.height()

        # 4. Get Mouse Position (Screen & Map)
        screen_pos = event.pos()

        # Transform pixels to map coordinates
        map_point = canvas.getCoordinateTransform().toMapCoordinates(screen_pos)

        # 5. Calculate New Extent Size
        # We divide by the factor.
        # If factor is 1.25 (Zoom In), size gets smaller.
        # If factor is 0.8 (Zoom Out), size gets bigger.
        new_width = current_extent.width() / factor
        new_height = current_extent.height() / factor

        # 6. Calculate Screen Ratios
        # Where is the mouse relative to the screen width/height? (0.0 to 1.0)
        ratio_x = screen_pos.x() / canvas_width
        ratio_y = screen_pos.y() / canvas_height

        # 7. Calculate New Extent Coordinates
        # We position the new extent so the map_point aligns with the screen ratios
        new_xmin = map_point.x() - (new_width * ratio_x)
        new_xmax = new_xmin + new_width

        # Y-Axis Logic (Screen Y is inverted relative to Map Y)
        new_ymax = map_point.y() + (new_height * ratio_y)
        new_ymin = new_ymax - new_height

        # 8. Apply Extent
        new_extent = QgsRectangle(new_xmin, new_ymin, new_xmax, new_ymax)
        canvas.setExtent(new_extent)
        canvas.refresh()
