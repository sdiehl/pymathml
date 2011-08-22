
class Plotter:
    """Abstract MathML rendering interface"""

    def setfont(self, family, style, size):
	"""Changes to the font described by @family, @style, and @size."""

    def labelmetrics(self, text):
	'''Returns the dimmensions of the text string @text, without
	actually drawing it.

	@text should be either a string object in UTF-8 encoding, or a
	unicode object. In either case, the plotter is responsible for
	automatically loading alternative fonts for characters, such
	as symbols, not found in the currently selected font.

	Returns: layout, width, height, axis.

	The plotter is allowed to request caching of layout
	information between calls to labelmetrics() and label() by
	returning a "layout" object to the caller. The returned
	@layout value should be passed back by the caller to label(),
	whenever possible.

	width = text width;
	height = ascender + descender;
	width and height should be a bounding box as tight as possible

	axis is the axis position of the text, relative to the bottom
	of the text.  '''

    def moveto(self, x, y):
	"""Changes the pen position to the point (@x, @y)."""

    def label(self, text, layout=None):
	"""Draws the text string @text at the current pen
	position. Horizontal alignment should be 'left'. Vertical
	alignment should be 'baseline'. @layout can be a layout cache
	value returned by labelmetrics(), or None if not available.
	In the end, the pen is left at the end of the text."""

    def savestate(self):
	"""Saves the current graphics state in a stack"""

    def restorestate(self):
	"""Restores the graphics state from the stack."""

    def translate(self, x, y):
	"""Adds a translation to the coordinate system for all future
	rendering operations."""

    def linewidth(self, width):
	"""Sets the line width, or thickness, for future line drawing
	operations."""

    def lineto(self, x, y):
	"""Draws a line from the current pen position to the point
	(@x, @y).  The end point becomes the new pen position."""

    def resolve_length(self, value, unit):
	"""Converts a value with unit to an absolute length in plotter
	coordinates.
	@value is a float, the numeric part;

	@unit is a string with the abbreviated unit name, such as 'pt'
	"""

    def setcliprect(self, x1, y1, x2, y2):
	"""Sets a clipping rectangle.  It remains in effect until
	restorestate() is called."""


