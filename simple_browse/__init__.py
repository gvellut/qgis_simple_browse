def classFactory(iface):  # pylint: disable=invalid-name
    from .simple_browse import SimpleBrowsePlugin

    return SimpleBrowsePlugin(iface)
