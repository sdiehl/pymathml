#! /usr/bin/env python
import pygtk
pygtk.require("2.0")

import sys, os.path
sys.path.insert(0, os.path.dirname(sys.argv[0]))

import gtk, gtk.gdk
import pango
import mathml, mathml.xml.sax_parser as fromxml
from mathml.backend.gdk_pango import *
#from mathml.backend.nxplot_mathml import *
import xml.sax
from cStringIO import StringIO

window = gtk.Window(gtk.WINDOW_TOPLEVEL)
canvas = gtk.DrawingArea()
canvas.set_size_request(640, 480)
window.add(canvas)
window.set_property("border-width", 4)


class Test:
    def create_plotter(self, darea):
	pass
    def set_mathml_tree(self, root):
	self.root = root
    def post_setup(self):
	pass
    def render_common(self):
	root = self.root
	root.x0 = 100
	root.y0 = 100
	root.setAttribute("fontsize", "40pt")
	root.update()
	root.render()
	root.plotter.linewidth(1)
	# axis indicator
	root.plotter.moveto(0, root.y0 + root.axis)
	root.plotter.lineto(root.x0 - 4, root.y0 + root.axis)
	root.plotter.moveto(root.x0 + root.width + 4, root.y0 + root.axis)
	root.plotter.lineto(root.plotter.width, root.y0 + root.axis)

	# corners
	x1, y1 = root.x0, root.y0
	x2, y2 = root.x0 + root.width, root.y0 + root.height
	W = 10
	#  bottom-left
	root.plotter.moveto(x1, y1 + W)
	root.plotter.lineto(x1, y1)
	root.plotter.lineto(x1 + W, y1)
	#  bottom right
	root.plotter.moveto(x2 - W, y1)
	root.plotter.lineto(x2, y1)
	root.plotter.lineto(x2, y1 + W)
	#  top right
	root.plotter.moveto(x2, y2 - W)
	root.plotter.lineto(x2, y2)
	root.plotter.lineto(x2 - W, y2)
	#  top left
	root.plotter.moveto(x1 + W, y2)
	root.plotter.lineto(x1, y2)
	root.plotter.lineto(x1, y2 - W)


class GtkTest(Test):
    def create_plotter(self, darea):
	self.pl = GtkPlotter(darea)
	self.darea = darea
	return self.pl

    def post_setup(self):
	canvas.connect("size-allocate", self._size_allocate)

    def _render(self):
	self.render_common()
	self.darea.queue_draw()
	return 0
    
    def _size_allocate(self, canvas, allocation):
	self.pl.width = allocation.width
	self.pl.height = allocation.height
	gtk.idle_add(self._render)


class NxplotTest(Test):
    def _get_resolution(self):
	resolution_mm = (gtk.gdk.screen_height() /
			 float(gtk.gdk.screen_height_mm()))
	resolution_pt = resolution_mm * 0.3514598;
	return resolution_pt
    
    def create_plotter(self, darea):
	self.nxplot_pl = NxplotArtft(darea)
	resolution_pt = self._get_resolution()
	print "resolution_pt", resolution_pt
	self.pl = NxplotPlotter(self.nxplot_pl, resolution_pt)
	self.darea = darea
	return self.pl
    
    def _render(self, pl):
	self.pl.width = self.darea.allocation.width
	self.pl.height = self.darea.allocation.height
	pl.open();
	pl.space(0, 0, self.pl.width, self.pl.height)
	pl.erase();
	self.render_common()
	pl.close();

    def post_setup(self):
	self.nxplot_pl.connect_after('update', self._render)
    
	
try:
    driver = sys.argv[1]
except IndexError:
    driver = 'gtk'

test = GtkTest()

pl = test.create_plotter(canvas)

root = fromxml.parseString('''
<math xmlns="http://www.w3.org/1998/Math/MathML"> 
  <mfrac> 
    <mrow> 
      <mi> x </mi> 
      <mo> + </mo> 
      <mi> y </mi> 
      <mo> + </mo> 
      <mi> z </mi> 
    </mrow> 
    <mrow> 
      <mi> x </mi> 
      <mo> + </mo> 
      <mi> z </mi> 
    </mrow> 
  </mfrac> 
</math>

''', pl)

test.set_mathml_tree(root)
test.post_setup()

window.connect("destroy", lambda x: gtk.main_quit())
window.show_all()
gtk.main()

