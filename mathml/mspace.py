from element import Element, xml_mapping
import warnings

class MSpace(Element):
    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	assert len(children) == 0

    def update(self):
        self.width = self.getAttribute("width", recursive=0, default="0").asLength()
        height = self.getAttribute("height", recursive=0, default="0").asLength()
        depth = self.getAttribute("depth", recursive=0, default="0").asLength()
        self.height = height + depth
        self.axis = depth

    def draw(self):
        pass

    def embellished_p(self):
        return None

xml_mapping['mspace'] = MSpace

