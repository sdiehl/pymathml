from __future__ import generators
import re, math, weakref
from plotter import Plotter
import events


class Element(events.EventSource):
    """Class representing any MathML element"""

    class Attribute:

	_length_rx = re.compile(r'^(?P<number>-?(?:\d+(?:\.\d+)?|\.\d+)'
				r'(?:[eE][+-]?\d+)?)(?P<unit>[a-zA-Z]{1,2})?$')

	def __init__(self, elem, value):
	    self.__element = weakref.ref(elem)
	    self.__value = value

	def __get_element(self):
	    return self.__element()

	element = property(__get_element, None, None,
			   "The element this attribute belongs to")

	def asFloat(self):
	    if isinstance(self.__value, float):
		return self.__value
	    self.__value = float(self.__value)
	    return self.__value
	    
	def asInt(self):
	    if isinstance(self.__value, int):
		return self.__value
	    self.__value = int(self.__value)
	    return self.__value

	def asBoolean(self):
	    if isinstance(self.__value, int):
		return self.__value
	    if self.__value == 'true':
		val = 1
	    elif self.__value == 'false':
		val = 0
	    else:
		val = int(self.__value)
	    self.__value = val
	    return val

	def asLength(self, default_unit_scale=1.0):
	    if isinstance(self.__value, float):
		return self.__value
	    # Now we try to convert the string to a numeric length
	    assert isinstance(self.__value, str) or \
		   isinstance(self.__value, unicode)
	    m = self._length_rx.match(self.__value)
	    if not m:
		# Try to dereference symbolic length constants
		attr = self.element.getAttribute(self.__value, 1)
		if attr is None:
		    raise ValueError("Cannot parse string \"%s\" as length" % (self.__value))
		else:
		    return attr.asLength()
	    number = m.group('number')
	    unit   = m.group('unit')
	    if unit is None:
		value = float(number) * default_unit_scale
	    elif unit == "pt":
		value = self.element.plotter.resolve_length(float(number), unit)
	    elif unit == 'ex':
		value = float(number) * self.element.font_size # FIXME: not 100% correct
	    elif unit == 'em':
		value = float(number) * self.element.font_size
		#print "float(number) * self.element.font_size", float(number) , self.element.font_size
	    else:
		raise RuntimeError("Parsing of unit '%s' is not implemented" % (unit, ))
	    self.__value = value	# cache result
	    return value

	float  = property(asFloat,   None, None, "Value as float")
	int    = property(asInt,     None, None, "Value as integer")
	bool   = property(asBoolean, None, None, "Value as boolean")
	length = property(asLength,  None, None, "Value as length")

	def asString(self):
	    if isinstance(self.__value, float):
		return self.__value
	    self.__value = str(self.__value)
	    return self.__value

	def __str__(self):
	    return str(self.__value)

	str = property(asString, None, None, "Value as string")


    def __init__(self, plotter):
	assert isinstance(plotter, Plotter)
        events.EventSource.__init__(self)
	self.__attributes = {}
	self.__children   = []
	self.__font_size  = None
	self.axis         = None
	self.width        = None
	self.height       = None
	self.x0           = None
	self.y0           = None
	self.needs_update = 1
	self.parent       = None
	self.plotter      = plotter
	self._script_level = None
	
    def __iter__(self):
	return iter(self.__children)

    def addChild(self, child, pos=None):
	if pos is None:
	    self.__children.append(child)
	else:
	    self.__children.insert(pos, child)
	child.parent = self

    def getChildren(self):
	return tuple(self.__children)

    children = property(getChildren, None, None, "list of child elements")

    def getAllChildren(self):
	for child in self.__children:
	    yield child
	yield self

    all_children = property(getAllChildren, None, None, "recursively expanded"
			    " list, depth-first, of child elements")
    
    def setAttribute(self, name, value):
	"""Sets the MathML attribute @name to value @value"""
	self.__attributes[name] = self.Attribute(self, value)

    def setAttributeWeak(self, name, value):
	"""Like setAttribute, but the value is set only if it is not
	already defined"""
	if not self.__attributes.has_key(name):
	    self.__attributes[name] = self.Attribute(self, value)

    def getAttribute(self, name, recursive=1, default=None):
	"""Lookup an attribute. Returns an Element.Attribute instance"""
	assert isinstance(name, str) or isinstance(name, unicode), \
	       "type(name) == %s (value=%s) != str" % (str(type(name)), str(name))
	try:
	    attr = self.__attributes[name]
	except KeyError:
	    if recursive:
		if self.parent is not None:
		    attr = self.parent.getAttribute(name)
		else:
		    attr = None
	    else:
		attr = None
	if attr is None and default is not None:
	    attr = self.Attribute(self, default)
	return attr

    def __delFontSize(self):
	self.__font_size = None

    def getScriptLevel(self):
	if self._script_level is not None:
	    return self._script_level
	scriptlevel = self.getAttribute("scriptlevel", recursive=0)
	if scriptlevel is None:
	    self._script_level = self.parent.getScriptLevel()
	else:
	    scriptlevel = scriptlevel.str
	    if scriptlevel[0] == '+' or scriptlevel[0] == '-':
		# relative scriptlevel
		self._script_level = self.parent.getScriptLevel() + \
				     int(scriptlevel)
	    else:
		self._script_level = int(scriptlevel)
	return self._script_level

    def getFontSize(self):
	""" font size computation is a bit expensive, so we cache its
	 value across invocations.  Should the value need to be
	 recomputed, it should be deleted first with del
	 self.font_size"""
	if self.__font_size is not None:
	    return self.__font_size
	attr = self.getAttribute("fontsize")
	fontsize, fontsize_elem = attr.length, attr.element
	fontsize_scriptlevel = fontsize_elem.getScriptLevel()
	scriptlevel = self.getScriptLevel()
	if self.parent:
	    scriptsizemultiplier = self.parent.getAttribute("scriptsizemultiplier").float
	else:
	    scriptsizemultiplier = self.getAttribute("scriptsizemultiplier").float
	return fontsize*math.pow(scriptsizemultiplier, scriptlevel - fontsize_scriptlevel);

    font_size = property(getFontSize, None, __delFontSize,
			 "Font size (max text height) for this element")

    def update(self):
	"""Updates the element, which consists of:

	1. Possibly setting some attributes on the element's children,
           such as 'scriptlevel';

	2. Calling update() on the element's children;

	3. Performing layout, i.e. setting the x0 and y0 attributes of
	the children;

	4. Compute the element's bounding box and store the result
	in self.width and self.height.

	All this is done assuming that the element is to be drawn
	starting at (0, 0), and its childrens' coordinates are set
	relative to this origin.

	Warning: self.x0 and self.y0 are not to be changed, or even
	consulted!"""

    def draw(self):
	"""Draws the element, but only this element, not its children!

	The element is to be drawn starting at (0, 0)."""

    def render(self):
	if self.x0 is not None:
	    self.plotter.savestate()
	    self.plotter.translate(self.x0, self.y0)
	for child in self:
	    child.render()
	if self.x0 is not None:
	    self.draw()
	    self.plotter.restorestate()

    isSpaceLike = 0


    def embellished_p(self):
	"""Returns embellished core, if this element is the container
	of an embellished operator, or None if not.

	This method should be overridden is subclasses whenever there
	is any chance that class can contain an embellished
	operator"""
	return None

    __embellished_computed = 0

    def __check_for_embellished_operator(self):
	core = self.embellished_p()
	if core is None:
	    for elem in self.all_children:
		elem.__embellished_container = None
		elem.__embellished_core      = None
		elem.__embellished_computed  = 1
	else:
	    for elem in self.all_children:
		elem.__embellished_container = self
		elem.__embellished_core      = core
		elem.__embellished_computed  = 1

    def getEmbellishedContainer(self):
	if not self.__embellished_computed:
	    self.__check_for_embellished_operator()
	return self.__embellished_container
	
    def getEmbellishedCore(self):
	if not self.__embellished_computed:
	    self.__check_for_embellished_operator()
	return self.__embellished_core

    embellished_container = property(getEmbellishedContainer, None, None,
				     "If this element is part of an embellished"
				     " operator group, the toplevel container"
				     " of that group")
    
    embellished_core = property(getEmbellishedCore, None, None,
				"If this element is part of an embellished"
				" operator group, the innermost operator"
				" element of that group")

# global dictionary mapping xml node names to classes
xml_mapping = {}

__all__ = ('Element',
	   'xml_mapping',
	   )
