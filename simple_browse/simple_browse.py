from __future__ import annotations

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .simple_browse_tool import SimpleBrowseMapTool


class SimpleBrowsePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.action: QAction | None = None
        self.tool: SimpleBrowseMapTool | None = None
        self._previous_tool = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icons", "simple_browse.svg")

        self.action = QAction(
            QIcon(icon_path), "Simple Browse", self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        self.action.triggered.connect(self._on_toggled)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Simple Browse", self.action)

        self.tool = SimpleBrowseMapTool(self.iface, self.action)

    def unload(self):
        canvas = self.iface.mapCanvas()

        if (
            self.tool
            and canvas.mapTool() == self.tool
            and self._previous_tool is not None
        ):
            canvas.setMapTool(self._previous_tool)

        if self.action:
            try:
                self.action.triggered.disconnect(self._on_toggled)
            except TypeError:
                pass

            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("&Simple Browse", self.action)

        self.tool = None
        self.action = None
        self._previous_tool = None

    def _on_toggled(self, checked: bool):
        if not self.tool:
            return

        canvas = self.iface.mapCanvas()

        if checked:
            self._previous_tool = canvas.mapTool()
            canvas.setMapTool(self.tool)
        else:
            if canvas.mapTool() == self.tool and self._previous_tool is not None:
                canvas.setMapTool(self._previous_tool)
