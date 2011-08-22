from element import *
from mrow import *
import math

class MRoot(Element):

    def __init__(self, plotter, children):
	assert len(children) == 2
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)
	self.row_strategy = MRow.Strategy()

    def _layout(self, base, index=None):
	self.base_width, self.base_height, base_axis = \
			 self.row_strategy.layout(base)
	self.spacing       = self.font_size / 10
	self.v_width       = max(self.base_height*.1, self.font_size/2)
	self.v_height      = self.base_height*0.5
	self.index_x_v_rel = self.v_width / 2
	self.linewidth     = self.font_size / 20;

	if index is not None:
	    self.v_start = max(0, index.width - self.index_x_v_rel)
	else:
	    self.v_start = 0

	if index is not None:
	    self.index_y = self.v_height + self.spacing*2
	    self.index_x = self.v_start + self.v_width*.6
	    index.x0 = self.index_x - index.width
	    index.y0 = self.index_y

	base_start = self.v_start + self.v_width + self.spacing
	for child in base:
	    child.x0 += base_start
	    child.y0 += self.spacing
	if math.fabs(base_axis/self.base_height - 0.5) < 0.1:
	    self.axis = base_axis + self.spacing
	else:
	    self.axis = self.base_height/2 + self.spacing
	self.width = (self.v_start + self.v_width +
		      self.spacing*2 + self.base_width)
	self.height = self.base_height + 3*self.spacing + self.linewidth/2
	if index is not None:
	    self.height = max(self.height, index.y0 + index.height)


    def update(self):
	assert len(self.children) == 2
	base, index = self.children
	index.setAttributeWeak("scriptlevel",  "+2")
	index.setAttributeWeak("displaystyle", "false")
	base.update()
	index.update()
	self._layout([base], index)

    def draw(self):
	top_line_y = int(self.base_height + self.spacing*3)
	self.plotter.linewidth(int(self.linewidth))
	self.plotter.moveto(int(self.v_start), int(self.v_height))
	self.plotter.lineto(int(self.v_start + self.v_width/2), int(0))
	self.plotter.lineto(int(self.v_start + self.v_width), int(top_line_y))
	self.plotter.lineto(int(self.v_start + self.v_width + self.spacing*2 + self.base_width), int(top_line_y))

class MSqrt(MRoot):
    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)
	self.row_strategy = MRow.Strategy()

    def update(self):
	for child in self.children:
	    child.update()
	self._layout(self.children, None)

    def embellished_p(self):
	return self.row_strategy.embellished_p(self.children)

xml_mapping['mroot'] = MRoot
xml_mapping['msqrt'] = MSqrt

