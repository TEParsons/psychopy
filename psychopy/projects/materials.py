import mimetypes
import wx

__all__ = [
    "schemaTypes",
    "AttributionDlg"
]

# map mimetypes to schema object types
schemaTypes = {
}
for val in mimetypes.types_map.values():
    # match all video types to VideoObject
    if val.startswith("video/"):
        schemaTypes[val] = "VideoObject"
    # match all image types to ImageObject
    if val.startswith("image/"):
        schemaTypes[val] = "ImageObject"
    # match all audio types to AudioObject
    if val.startswith("audio/"):
        schemaTypes[val] = "AudioObject"
    # match all font types to generic CreativeWork
    if val.startswith("font/"):
        schemaTypes[val] = "CreativeWork"

class AttributionDlg(wx.Dialog):
    def __init__(self, materials):
        # initialize parent class
        wx.Dialog.__init__(self, None, style=wx.OK | wx.CANCEL)
        # copy materials list so we don't affect the original
        self.materials = materials.copy()

    def getMaterials(self):
        return []

