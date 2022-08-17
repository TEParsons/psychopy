from psychopy.localization import _translate

# Known style / style tweaks options for Slider
sliderStyleOptions = {}
sliderStyleOptions.knownStyles = {
    'slider': _translate("Slider"),
    'rating': _translate("Rating"),
    'radio': _translate("Radio"),
    'scrollbar': _translate("Scrollbar")
}
sliderStyleOptions.legacyStyles = {}
sliderStyleOptions.knownStyleTweaks = {
    'labels45': _translate("Rotate labels 45º"),
    'triangleMarker': _translate("Triangular marker")
}
sliderStyleOptions.legacyStyleTweaks = {
    'whiteOnBlack': _translate("White on black")
}
