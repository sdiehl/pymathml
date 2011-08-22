from element import *
import warnings

class MFrac(Element):
    def __init__(self, plotter, children):
	assert len(children) == 2
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)

    def update(self):
	numerator, denominator = self.children
	for child in numerator, denominator:
	    if child.getAttribute("displaystyle", default="false").bool:
		child.setAttribute("displaystyle", "false")
	    else:
		child.setAttribute("scriptlevel", "+1")

	self.linethickness = self.getAttribute("linethickness", recursive=0,
					       default="1").float
	numalign      = intern(self.getAttribute("numalign", recursive=0,
						 default="center").str)
	denomalign    = intern(self.getAttribute("denomalign", recursive=0,
						 default="center").str)
	beveled       = self.getAttribute("bevelled", recursive=0,
					  default="false").bool
	if beveled:
	    warnings.warn("<mfrac bevelled=\"true\"> not yet implemented.")

	self.linethickness *= .05*self.font_size
	vspace = self.font_size*.2

	numerator.update()
	denominator.update()

	max_width = max(numerator.width, denominator.width)
	hspace = self.font_size*.15
	def halign(elem, width, alignment):
	    if alignment == 'left':
		elem.x0 = 0
	    elif alignment == 'center':
		elem.x0 = width/2 - elem.width/2
	    elif alignment == 'right':
		elem.x0 = width - elem.width
	    else:
		warnings.warn("Invalid alignment '%s' in mfrac" % (alignment, ))
	# horizontal alignment and size
	halign(numerator, max_width, numalign)
	numerator.x0 += hspace
	halign(denominator, max_width, denomalign)
	denominator.x0 += hspace
	self.width = max_width + 2*hspace
	# vertical alignment and size
	denominator.y0 = 0
	self.axis = denominator.height + vspace
	numerator.y0 = self.axis + vspace
	self.height = numerator.y0 + numerator.height

    def draw(self):
	self.plotter.linewidth(int(self.linethickness))
	self.plotter.moveto(0, self.axis)
	self.plotter.lineto(self.width, self.axis)

    def embellished_p(self):
	try:
	    return self.children[0].embellished_p()
	except IndexError:
	    return None

xml_mapping['mfrac'] = MFrac

