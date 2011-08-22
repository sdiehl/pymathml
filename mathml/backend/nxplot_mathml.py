# This driver uses the Nxplot 2D library, which can be found in the
# numexp project http://numexp.sf.net
# Nxplot itself uses FreeType and libart_lgpl or GnomePrint.

from nxplot import *
import mathml
import warnings



class NxplotPlotter(mathml.plotter.Plotter):
    SYMBOL_FONT     = "Standard Symbols L Regular"
    _font_axis_rel_pos = {
	SYMBOL_FONT: 0.22
	}
    _font_axis_rel_pos_default = 0.27

    def __init__(self, pl, pt_resolution):
	"""@pl: a Nxplot instance;
	@pt_resolution: nxplot units per 'point' (pt)"""
	self.pl = pl
	self.pt_resolution = pt_resolution

    def moveto(self, x, y):
	self.pl.move(x, y)
	self.last_x = x
	self.last_y = y

    def lineto(self, x, y):
	self.pl.line(self.last_x, self.last_y, x, y)
	self.last_x = x
	self.last_y = y

    def linewidth(self, width):
	self.pl.linewidth(width)

    def setfont(self, family, style, size):
	self.fontname = ' '.join((family, style))
	self.pl.fontname(self.fontname)
	self.pl.fontsize(size)
	self.font_size = size

    def labelmetrics(self, text):
	#Returns: layout, width, height, axis
	try:
	    axis_rel_pos = self._font_axis_rel_pos[self.fontname]
	except KeyError:
	    axis_rel_pos = self._font_axis_rel_pos_default
	(ascender_max, descender_max,
	 ascender, descender, width) = self.pl.labelmetrics(text)
	axis = ascender_max*axis_rel_pos
	return (descender, # callback data
		width, descender + ascender,
		descender + axis)

    def label(self, text, layout=None):
	if layout is None:
	    (descender, width,
	     height, axis) = self.labelmetrics(text)
	else:
	    descender = layout
	self.pl.moverel(0, descender)
	self.pl.label(HAlign.LEFT, VAlign.BASELINE, text)
	self.pl.moverel(0, -descender)

    def savestate(self):
	self.pl.savestate()

    def restorestate(self):
	self.pl.restorestate()

    def translate(self, x, y):
	self.pl.translate(x, y)

    def resolve_length(self, value, unit):
	if unit == 'pt':
	    return self.pt_resolution * value
	warnings.warn("Cannot resolve unit '%s'" % (unit, ))
	return value

    def setcliprect(self, x1, y1, x2, y2):
	self.pl.setcliprect(NxplotRect(x1, y1, x2, y2))

