from element import *
from mrow    import MRow

_default_math_attributes = {
    "fontsize":			"12pt",
    "scriptlevel":      	"0",
    "scriptsizemultiplier":	"0.71",
    "scriptminsize":		"8pt",
    "veryverythinmathspace":	"0.0555556em",
    "verythinmathspace":	"0.111111em",
    "thinmathspace":		"0.166667em",
    "mediummathspace":		"0.222222em",
    "thickmathspace":		"0.277778em",
    "verythickmathspace":	"0.333333em",
    "veryverythickmathspace":	"0.388889em",
}

class Math(Element):
    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	self.strategy = MRow.Strategy()
	for child in children:
	    self.addChild(child)
	for key, val in _default_math_attributes.iteritems():
	    self.setAttribute(key, val)

    def update(self):
	if not self.needs_update: return
	self.needs_update = 0

	display = self.getAttribute("display", default="inline").str
	if display == 'inline':
	    self.setAttributeWeak("displaystyle", False)
	elif display == 'block':
	    self.setAttributeWeak("displaystyle", True)
	else:
	    raise ValueError("<math> display attribute must be"
			     " 'block' or 'inline', not '%s'" % display)

	self.strategy.modify_children(self.children)
	for child in self: child.update()
	self.width, self.height, self.axis = self.strategy.layout(self.children)

    def embellished_p(self):
	return self.strategy.embellished_p(self.children)

xml_mapping['math'] = Math

__all__ = [ 'Math' ]


