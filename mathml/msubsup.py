from element import *
import warnings
import munderover

_SUB_MAX_POSITION          = 1/3.0 # relative to the base height
_SUP_MIN_POSITION          = 2/3.0 # relative to the base height
_SUBSUP_MIN_DISTANCE       = 1/3.0 # relative to base's font size
_SCRIPT_HORIZONTAL_SPACING = 0.02  # relative to base's font size



class MSup(Element):

    class Strategy:

	def modify_children(elem, base, sup):
	    sup.setAttributeWeak("scriptlevel",  "+1")
	    sup.setAttributeWeak("displaystyle", "false")

	modify_children = staticmethod(modify_children)

	def layout(elem, base, sup):
	    base.x0 = 0
	    base.y0 = 0
	    sup.x0 = base.width + base.font_size*_SCRIPT_HORIZONTAL_SPACING
	    sup.y0 = max(base.height*_SUP_MIN_POSITION,
			 base.height - sup.axis)
	    elem.height = max(sup.y0 + sup.height, base.height)
	    elem.width = sup.x0 + sup.width
	    elem.axis = base.axis

	layout = staticmethod(layout)

    
    def __init__(self, plotter, children):
	assert len(children) == 2
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)

    def update(self):
	assert len(self.children) == 2
	base, sup = self.children

	## Honor attribute 'movablelimits'
	base.update()
	if (base.embellished_core is not None
	    and base.embellished_core.getAttribute("movablelimits",
						   recursive=False,
						   default=False)
	    and self.getAttribute("displaystyle").bool):
	    strategy = munderover.MOver.Strategy
	else:
	    strategy = self.Strategy

	strategy.modify_children(self, base, sup)
	sup.update()
	strategy.layout(self, base, sup)

    def embellished_p(self):
	try:
	    return self.children[0].embellished_p()
	except IndexError:
	    return None

class MSub(Element):

    class Strategy:

	def modify_children(elem, base, sub):
	    sub.setAttributeWeak("scriptlevel",  "+1")
	    sub.setAttributeWeak("displaystyle", "false")

	modify_children = staticmethod(modify_children)

	def layout(elem, base, sub):
	    base.x0 = 0
	    sub.x0 = base.width + base.font_size*_SCRIPT_HORIZONTAL_SPACING
	    sub.y0 = min(base.height*_SUB_MAX_POSITION - sub.height, -sub.axis)
	    base.y0 = -sub.y0
	    sub.y0  = 0
	    elem.height = max(sub.height, base.y0 + base.height)
	    elem.width = sub.x0 + sub.width
	    elem.axis = base.y0 + base.axis

	layout = staticmethod(layout)

    
    def __init__(self, plotter, children):
	assert len(children) == 2
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)

    def update(self):
	assert len(self.children) == 2
	base, sub = self.children

	## Honor attribute 'movablelimits'
	base.update()
	if (base.embellished_core is not None
	    and base.embellished_core.getAttribute("movablelimits",
						   recursive=False,
						   default=False)
	    and self.getAttribute("displaystyle").bool):
	    strategy = munderover.MUnder.Strategy
	else:
	    strategy = self.Strategy

	strategy.modify_children(self, base, sub)
	sub.update()
	strategy.layout(self, base, sub)
	
    def embellished_p(self):
	try:
	    return self.children[0].embellished_p()
	except IndexError:
	    return None

class MSubSup(Element):

    class Strategy:

	def modify_children(element, base, sub, sup):
	    for elem in sub, sup:
		elem.setAttributeWeak("scriptlevel",  "+1")
		elem.setAttributeWeak("displaystyle", "false")

	modify_children = staticmethod(modify_children)

	def layout(elem, base, sub, sup):
	    base.x0 = 0

	    # we assume initially that base.y0 = 0

	    sub.x0 = base.width + base.font_size*_SCRIPT_HORIZONTAL_SPACING
	    sub.y0 = min(base.height*_SUB_MAX_POSITION - sub.height, -sub.axis)

	    sup.x0 = sub.x0
	    sup.y0 = max(base.height*_SUP_MIN_POSITION,
			 base.height - sup.axis)

	    # then we offset all coordinates so that sub.y0 = 0
	    base.y0  = -sub.y0
	    sup.y0  -= sub.y0
	    sub.y0   = 0

	    # make sure the subscript and superscript are separated by
	    # a minimum distance
	    mindist = _SUBSUP_MIN_DISTANCE*base.font_size
	    dist = sup.y0 - (sub.y0 + sub.height)
	    if dist < mindist:
		delta = (mindist - dist)/2
		sub.y0 -= delta
		sup.y0 += delta

	    elem.height = max(sup.y0 + sup.height, base.y0 + base.height)
	    elem.width = sub.x0 + max(sub.width, sup.width)
	    elem.axis = base.y0 + base.axis

	layout = staticmethod(layout)
    
    def __init__(self, plotter, children):
	assert len(children) == 3
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)

    def update(self):
	assert len(self.children) == 3
	base, sub, sup = self.children

	## Honor attribute 'movablelimits'
	base.update()
	if (base.embellished_core is not None
	    and base.embellished_core.getAttribute("movablelimits",
						   recursive=False,
						   default=False)
	    and self.getAttribute("displaystyle").bool):
	    strategy = munderover.MUnderOver.Strategy
	else:
	    strategy = self.Strategy

	strategy.modify_children(self, base, sub, sup)
	sub.update()
	sup.update()
	strategy.layout(self, base, sub, sup)

    def embellished_p(self):
	try:
	    return self.children[0].embellished_p()
	except IndexError:
	    return None


xml_mapping['msup']    = MSup
xml_mapping['msub']    = MSub
xml_mapping['msubsup'] = MSubSup

