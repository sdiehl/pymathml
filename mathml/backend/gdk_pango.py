import gtk, gtk.gdk, pango
import mathml
from copy import *

class GtkPlotter(mathml.plotter.Plotter):

    class State:
	offset_x  = 0
	offset_y  = 0
	pen_x     = 0
	pen_y     = 0
	font_name = 'Sans'
	font_size = 10

    def __init__(self, widget):
	self.widget = widget
	self.width  = 0
	self.height = 0
	self.pixmap = None
	resolution_mm = (gtk.gdk.screen_height() /
			 float(gtk.gdk.screen_height_mm()))
	self.pt_resolution = resolution_mm * 0.3514598;
	print "self.pt_resolution", self.pt_resolution
	widget.connect('size-allocate', self._size_allocate_cb)
	widget.connect('realize', self._realize_cb)
	#widget.connect('expose-event', self._expose_event)
	self.state = self.State()
	self.saved_states = []
	self.pango_layout = pango.Layout(widget.get_pango_context())

    def _size_allocate_cb(self, widget, allocation):
	self.width = allocation.width
	self.height = allocation.height
	self.create_pixmap()

    def _realize_cb(self, widget):
	self.create_pixmap()
	self.gc = gtk.gdk.GC(widget.window)
	self.gc.copy(widget.style.fg_gc[widget.state])

    def reset(self):
	self.saved_states = []
	self.state = self.State()

    def create_pixmap(self):
	if self.widget.window is None: return
	self.pixmap = gtk.gdk.Pixmap(self.widget.window,
				     self.width, self.height, -1)
	self.pixmap.draw_rectangle(self.widget.style.bg_gc[self.widget.state],
				   gtk.TRUE, 0, 0, self.width, self.height)
	self.widget.window.set_back_pixmap(self.pixmap, 0)

    def _expose_event(self, widget, event):
	widget.window.draw_drawable(self.gc,
				    self.pixmap, event.area.x, event.area.y,
				    event.area.x, event.area.y,
				    event.area.width, event.area.height)

    def setfont(self, family, style, size):
	desc = family + ', ' + style + " " + str(size/self.pt_resolution)
	self.pango_layout.set_font_description(pango.FontDescription(desc))
	self.state.font_desc = desc
	self.font_size = size
	
    def labelmetrics(self, text):
	#Returns: layout, width, height, axis
	self.pango_layout.set_text(text)
	ink_rect, logical_rect = self.pango_layout.get_pixel_extents()
	x, y, width, height = logical_rect
	return None, width, height, self.font_size * .75
	

    def label(self, text, layout=None):
	self.pango_layout.set_text(text)
	ink_rect, logical_rect = self.pango_layout.get_pixel_extents()
	x, y, width, height = logical_rect
	wx = int(self._space2window_x(self.state.pen_x))
	wy = int(self._space2window_y(self.state.pen_y))
	#print ink_rect
	self.pixmap.draw_layout(self.gc, int(wx), int(wy - height - y), self.pango_layout)
	#self.pixmap.draw_line(self.widget.style.fg_gc[self.widget.state],
	#		      wx, wy, wx + 10, wy + 10)
	self.state.pen_x += width
	

    def savestate(self):
	self.saved_states.append(deepcopy(self.state))

    def restorestate(self):
	self.state = self.saved_states.pop()

    def translate(self, x, y):
	self.state.offset_x += x
	self.state.offset_y += y

    def moveto(self, x, y):
	self.state.pen_x = x
	self.state.pen_y = y

    def linewidth(self, width):
	self.gc.set_line_attributes(width, gtk.gdk.LINE_SOLID,
				    gtk.gdk.CAP_BUTT,
				    gtk.gdk.JOIN_MITER)

    def lineto(self, x, y):
	self.pixmap.draw_line(self.gc,
			      int(self._space2window_x(int(self.state.pen_x))),
			      int(self._space2window_y(int(self.state.pen_y))),
			      int(self._space2window_x(int(x))),
			      int(self._space2window_y(int(y))))
	self.state.pen_x = int(x)
	self.state.pen_y = int(y)

    def _space2window_x(self, x):
	return x + self.state.offset_x

    def _space2window_y(self, y):
	return 	self.height - (y + self.state.offset_y)

    def resolve_length(self, value, unit):
	if unit == 'pt':
	    return self.pt_resolution * value
	warnings.warn("Cannot resolve unit '%s'" % (unit, ))
	return value
