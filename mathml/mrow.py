from element import *
import mtoken

class MRow(Element):
    
    class Strategy:
	def layout(self, elements):
	    """Set positions of elements in a row;
	    Returns (width, height, axis) of row"""
	    global_axis             = 0
	    max_height_non_stretchy = 0
	    max_height_stretchy     = 0
	    max_depth_non_stretchy  = 0
	    max_depth_stretchy      = 0

	    # find out about axis, max height and max depth, for
	    # stretchy and non-stretchy operators

	    #print "Starting layout of an mrow (len=%i):---------" % len(elements)
	    
	    for elem in elements:
		if elem.axis is None:
		    elem.axis = elem.height/2
		if (elem is elem.embellished_container and
		    elem.embellished_core.getAttribute('stretchy', recursive=0,
						       default=0).bool):
		    max_height_stretchy = max(max_height_stretchy,
					      elem.height - elem.axis)
		    max_depth_stretchy = max(max_depth_stretchy, elem.axis)
		    #print "max_height_stretchy:", max_height_stretchy,\
		    #  "max_depth_stretchy:", max_depth_stretchy
		else:
		    max_height_non_stretchy = max(max_height_non_stretchy,
						  elem.height - elem.axis)
		    max_depth_non_stretchy = max(max_depth_non_stretchy,
						 elem.axis)
		    #print "max_height_non_stretchy:", max_height_non_stretchy,\
		    #	  "max_depth_non_stretchy:", max_depth_non_stretchy
		global_axis = max(global_axis, elem.axis)

	    # Stretch all stretchy operators
	    if max_height_non_stretchy == 0:
		height = max_height_stretchy
		depth  = max_depth_stretchy
	    else:
		height = max_height_non_stretchy
		depth  = max_depth_non_stretchy

	    #height = max(max_height_stretchy, max_height_non_stretchy)
	    #depth = max(max_depth_stretchy, max_depth_non_stretchy)
	    
	    #print "Final height, depth: ", height, depth
	    for elem in elements:
		#print elem, " => ", elem.embellished_container
		if elem is not elem.embellished_container:
		    continue
		core = elem.embellished_core
		if (core.getAttribute('stretchy', recursive=0,
				      default=0).bool):
		    #print core, "("+core.content+")", " => stretchy! (height=%f)" % core.height
		    if core.getAttribute('symmetric', recursive=0,
					 default=True).bool:
			core.setVStretch(max(height, depth),
					 max(height, depth))
			#print "Stretching ", core, "to (%f, %f)" % (max(height, depth),
			#					    max(height, depth))
		    else:
			core.setVStretch(height, depth)
			#print "Stretching ", core, "to (%f, %f)" % (height, depth)
		    elem.update()
		    global_axis = max(global_axis, elem.axis)
		#else:
		#    print core, "("+core.content+")", " => NOT stretchy! (height=%f)" % core.height

	    # OK, all set for final layout pass...
	    x = 0
	    height = 0
	    for elem in elements:
		if isinstance(elem, mtoken.MOperator):
		    # lspace
		    lspace = elem.getAttribute("lspace", recursive=False, default=0.0).asLength()
		    rspace = elem.getAttribute("rspace", recursive=False, default=0.0).asLength()
		else:
		    lspace = 0
		    rspace = 0
		x += lspace
		elem.x0 = x
		x += rspace
		x += elem.width
		elem.y0 = global_axis - elem.axis
		height = max(height, elem.y0 + elem.height)
	    return x, height, global_axis

	def modify_children(self, elements):
	    last_nonspace_index = -1
	    first_nonspace_index = -1

	    i = 0;
	    for child in elements:
		if not child.isSpaceLike:
		    last_nonspace_index = i
		    if first_nonspace_index == -1:
			first_nonspace_index = i
		i += 1
	    i = 0;
	    for child in elements:
		if child.isSpaceLike:
		    i += 1
		    continue
		if not isinstance(child, mtoken.MOperator):
		    i += 1
		    continue
		# If the operator is the first argument in an mrow of length
		# (i.e. number of arguments) greater than one (ignoring all
		# space-like arguments in the determination of both the length
		# and the first argument), the prefix form is used; 
		if i == first_nonspace_index:
		    form = "prefix"
		# if it is the last argument in an mrow of length greater
		# than one (ignoring all space-like arguments), the postfix
		# form is used; 
		elif i == last_nonspace_index:
		    form = "postfix"
		# in all other cases, including when the operator is not part
		# of an mrow, the infix form is used. 
		else:
		    form = "infix"
		child.setAttributeWeak("form", form)
		i += 1

	def embellished_p(self, children):
	    eopnum = 0
	    # an mrow whose arguments consist (in any order) of one
	    # embellished operator and zero or more space-like elements.
	    for elem in children:
		if elem.isSpaceLike: continue
		eopnum += 1
		if eopnum > 1: return None
		core = elem.embellished_p()
	    return core

    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)
	self.strategy = self.Strategy()

    def update(self):
	if not self.needs_update: return
	self.needs_update = 0
	self.strategy.modify_children(self.children)
	for child in self: child.update()
	self.width, self.height, self.axis = self.strategy.layout(self.children)

    def embellished_p(self):
	return self.strategy.embellished_p(self.children)

class MStyle(MRow): pass

xml_mapping['mrow']   = MRow
xml_mapping['mstyle'] = MStyle
