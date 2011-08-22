
import libxml2
from mathml.element import *
from mathml.mtoken import MToken


def parseTree(node, plotter):
    klass = xml_mapping[node.name]
    if issubclass(klass, MToken):
	element = klass(plotter, node.content.decode("utf-8").strip())
    else:
	children = []
	child = node.get_children()
	while child is not None:
	    if child.type != 'element':
		child = child.get_next()
		continue
	    children.append(parseTree(child, plotter))
	    child = child.get_next()
	element = klass(plotter, children)
    attr = node.get_properties()
    while attr is not None:
	if attr.type == 'attribute':
	    element.setAttribute(attr.name, attr.content)
	    attr = attr.next
    return element


def parseString(s, plotter):
    ctxt = libxml2.createMemoryParserCtxt(s, len(s))
    #ctxt.replaceEntities(1)
    #ctxt.loadSubset(1)
    #ctxt.validate(1) # should be set to 0 for greater speed
    ctxt.parseDocument()
    if not ctxt.wellFormed():
	print "Document not well formed!"
    if not ctxt.isValid():
	print "Document not valid!"
    doc = ctxt.doc()
    root = doc.children
    assert root.name == 'math'
    return parseTree(root, plotter)

