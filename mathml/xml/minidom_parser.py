
import xml.dom.minidom as dom
from mathml.element import *
from mathml.mtoken import MToken


def parseTree(node, plotter):
    assert node.nodeType == node.ELEMENT_NODE
    klass = xml_mapping[node.tagName]
    if issubclass(klass, MToken):
	content = "".join([child.data for child in node.childNodes
			   if child.nodeType == child.TEXT_NODE])
	if not isinstance(content, unicode):
	    content = content.decode("utf-8")
	element = klass(plotter, content.strip())
    else:
	children = []
	for child in node.childNodes:
	    if child.nodeType != child.ELEMENT_NODE:
		continue
	    children.append(parseTree(child, plotter))
	element = klass(plotter, children)
    attrs = node.attributes
    for i in xrange(attrs.length):
	attr = attrs.item(i)
	element.setAttribute(attr.name, attr.value)
    return element


def parseString(s, plotter):
    doc = dom.parseString(s)
    root = doc.documentElement
    if root.tagName != 'math':
	raise RuntimeError("Not a mathml document")
    return parseTree(root, plotter)

