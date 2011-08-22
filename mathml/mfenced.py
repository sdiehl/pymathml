from element import *
import mrow
from mtoken import MOperator
import re

'''
The general mfenced element shown above is equivalent to the following expanded form:

<mrow>
   <mo fence="true"> opening-fence </mo>
   <mrow>
      arg#1
      <mo separator="true"> sep#1 </mo>
      ...
      <mo separator="true"> sep#(n-1) </mo>
      arg#n
   </mrow>
   <mo fence="true"> closing-fence </mo>
</mrow>
'''

_whitespace_rx = re.compile("\\s+")

class MFenced(mrow.MRow):
    def __init__(self, plotter, children):
	self.__children = children
	# postpone adding of children until the first update, since we
	# have not yet received the xml attributes.
	super(MFenced, self).__init__(plotter, [])

    def __addChildren(self, children):
	open  = MOperator(self.plotter, self.getAttribute(
	    "open", recursive=False, default="(").str)
	close = MOperator(self.plotter, self.getAttribute(
	    "close", recursive=False, default=")").str)
	open.setAttribute("fence", True)
	close.setAttribute("fence", True)

	separators = self.getAttribute("separators", recursive=False, default=",").str

	inner_row = []
	for i, child in enumerate(children):
	    inner_row.append(child)
	    if i < len(children) - 1:
		try:
		    sep = separators[i]
		except IndexError:
		    sep = separators[-1]
		sep = MOperator(self.plotter, sep)
		sep.setAttribute("separator", True)
		inner_row.append(sep)

	if len(inner_row) == 0:
	    new_children = [open, close]
	elif len(inner_row) == 1:
	    new_children = [open, inner_row[0], close]
	else:
	    new_children = [open, mrow.MRow(self.plotter, inner_row), close]

	for child in new_children:
	    self.addChild(child)

    def update(self):
	try:
	    children = self.__children
	except AttributeError:
	    children = None
	if children is not None:
	    self.__addChildren(children)
	    del self.__children
	super(MFenced, self).update()
	

xml_mapping['mfenced'] = MFenced
