import numpy

COLORS = {
    "🟥": [numpy.array([231, 46, 40])],
    "🟧": [numpy.array([239, 101, 5])],
    "🟨": [numpy.array([246, 212, 14]), numpy.array([239, 226, 164])],
    "🟩": [numpy.array([0, 255, 0])],
    "🟦": [numpy.array([74, 136, 241]), numpy.array([3, 60, 102])],
    "🟪": [numpy.array([137, 102, 202]), numpy.array([167, 141, 128])],
    "🟫": [numpy.array([104, 69, 50])],
    "⬛": [numpy.array([0, 0, 0]), numpy.array([30, 30, 30])],
    "⬜": [numpy.array([228, 228, 228]), numpy.array([188, 188, 212])],
}

COLOR_VALUES = []
COLOR_KEYS = []
for color, rgbs in COLORS.items():
    for rgb in rgbs:
        COLOR_VALUES.append(rgb)
        COLOR_KEYS.append(color)
COLOR_VALUES = numpy.asarray(COLOR_VALUES)

def image_to_text(pixels : tuple) -> str:
    row = ""
    for pixel in pixels:
        row += COLOR_KEYS[numpy.linalg.norm(COLOR_VALUES - pixel, axis=-1).argmin()]
        
    return row