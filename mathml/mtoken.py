from element import *
import warnings
import opdict
import re

# --- FONT NAMES ---
if 0:
    # experimental fonts...
    MI_FONT_REGULAR = ('Sans', 'Regular')
    MI_FONT_ITALIC  = ('Sans', 'Italic')
    MO_FONT_REGULAR = ('Sans', 'Regular')
    MO_FONT_ITALIC  = ('Sans', 'Italic')
    MN_FONT         = ('Sans', 'Regular')
    MTEXT_FONT      = ('Sans', 'Regular')
    MERROR_FONT     = ('Monospace', 'Regular')
elif 0:
    # experimental fonts...
    MI_FONT_REGULAR = ('cmr10', 'Regular')
    MI_FONT_ITALIC  = ('cmmi10', 'Regular')
    MO_FONT_REGULAR = ('cmr10', 'Regular')
    MO_FONT_ITALIC  = ('cmmi10', 'Regular')
    MN_FONT         = ('cmr10', 'Regular')
    MTEXT_FONT      = ('Sans', 'Regular')
    MERROR_FONT     = ('Monospace', 'Regular')
else:
    MI_FONT_REGULAR = ('URW Palladio L', 'Roman')
    MI_FONT_ITALIC  = ('URW Palladio L', 'Italic')
    MO_FONT_REGULAR = ('URW Palladio L', 'Roman')
    MO_FONT_ITALIC  = ('URW Palladio L', 'Italic')
    MN_FONT         = ('URW Bookman L', 'Light')
    MTEXT_FONT      = ('Serif', 'Regular')
    MERROR_FONT     = ('Times', 'Regular')




class _StretchyParts(object):
    __slots__ = ('upper', 'lower', 'middle', 'bar')
    def __init__(self, upper, lower, bar, middle=None):
	self.upper  = upper
	self.lower  = lower
	self.middle = middle
	self.bar    = bar
	

# pieces that make up a stretchy operator: upper, middle, and lower parts.
_stretchy_parenthesis = {
    '(': _StretchyParts(upper=unichr(0xf8eb), bar=unichr(0xf8ec), lower=unichr(0xf8ed)),
    '[': _StretchyParts(upper=unichr(0xf8ee), bar=unichr(0xf8ef), lower=unichr(0xf8f0)),
    '{': _StretchyParts(upper=unichr(0xf8f1), middle=unichr(0xf8f2),
			lower=unichr(0xf8f3), bar=unichr(0xf8f4)),
    ')': _StretchyParts(upper=unichr(0xf8f6), bar=unichr(0xf8f7), lower=unichr(0xf8f8)),
    ']': _StretchyParts(upper=unichr(0xf8f9), bar=unichr(0xf8fa), lower=unichr(0xf8fb)),
    '}': _StretchyParts(upper=unichr(0xf8fc), middle=unichr(0xf8fd),
			lower=unichr(0xf8fe), bar=unichr(0xf8f4)),
    unichr(0x222B): _StretchyParts(upper=unichr(0x2320),
				   lower=unichr(0x2321),
				   bar=unichr(0xf8f5)), # integral
    '|': _StretchyParts(upper=unichr(0xf8f5), lower=unichr(0xf8f5), bar=unichr(0xf8f5)),
    }

content_substitutions = {
    unichr(0x02145): 'D', # &CapitalDifferentialD;
    unichr(0x02146): 'd', # &DifferentialD;
    unichr(0x02147): 'e', # &ExponentialE;
    unichr(0x02148): 'i', # &ImaginaryI;
    '-':             u'\N{MINUS SIGN}',
    unichr(0x02AA1): u'\N{MUCH LESS-THAN}', # &LessLess;
    unichr(0x02AA2): u'\N{MUCH GREATER-THAN}', # &GreaterGreater;
    unichr(0x02254): u'\N{COLON EQUALS}', # assignment operator
    }

_content_substitutions_rx = re.compile("|".join(map(re.escape, content_substitutions.keys())))


# --------------------------------------------------------

class MToken(Element):

    def __init__(self, plotter, content):
	Element.__init__(self, plotter)
	self.content = content	
	self.descender = 0
	self.__stretch_height = None
	self.__stretch_depth  = None
	self.__stretch_width  = None
	self.__parts = None
	self.__stretchy_font_family = "Standard Symbols L"
	self.__stretchy_font_style = "Regular"
	if (self.content == unichr(0x2062) or # &InvisibleTimes;
	    self.content == unichr(0x2061)    # &ApplyFuncion;
	    ):
	    self.setAttributeWeak("lspace", 0.0)
	    self.setAttributeWeak("rspace", 0.0)
	self._applySubstitutions()

    def _applySubstitutions(self):
	self.subst_content = _content_substitutions_rx.sub(
	    lambda match: content_substitutions[match.group(0)], self.content)
	
    def _update_stretchy(self):
	pl = self.plotter

	pl.setfont(self.__stretchy_font_family,
		   self.__stretchy_font_style,
		   self.font_size)
	default_min_height = 0
	for part in (self.__parts.lower,
		     self.__parts.middle,
		     self.__parts.upper):
	    if part is None: continue
	    _, _, height, _ = pl.labelmetrics(part)
	    default_min_height += height

	# make sure font is never shrinked more than half, even if
	# that means stretching a bit more than requested.
	if default_min_height*0.5 > self.__stretch_depth + self.__stretch_height:
	    self.height = default_min_height*0.5
	    k = self.__stretch_depth / (self.__stretch_depth + self.__stretch_height)
	    self.__stretch_depth = self.height*k
	    self.__stretch_height = self.height - self.__stretch_depth
	    self.__stretched_font_size = self.font_size*0.5
	else:
	    self.height = self.__stretch_depth + self.__stretch_height
	    if default_min_height > self.height:
		self.__stretched_font_size = self.height/default_min_height*self.font_size
	    else:
		self.__stretched_font_size = self.font_size

	pl.setfont(self.__stretchy_font_family,
		   self.__stretchy_font_style,
		   self.__stretched_font_size)
	_, self.width, _, _ = pl.labelmetrics(self.__parts.bar)
	self.width *= 1.15		# stupid fonts!

	self.axis = self.__stretch_depth
	
    def update(self):
	# Delegate horizontal/vertical stretching
	if self.__stretch_width:
	    return self._update_hstretchy()
	elif self.__parts is not None:
	    return self._update_stretchy()

	if (self.content == unichr(0x2062) or # &InvisibleTimes;
	    self.content == unichr(0x2061)):  # &ApplyFunction;
	    self.width=self.Attribute(self, "verythinmathspace").length
	    self.height=0
	    return
	
	pl = self.plotter
	pl.setfont(self.font_family, self.font_style, self.font_size)
	self.__layout_cache, self.width, self.height, self.axis =\
		pl.labelmetrics(self.subst_content)
	self.unstretched_width  = self.width
	self.unstretched_height = self.height

    def setVStretch(self, height, depth):
	#print "setVStrectch(height=%f, depth=%f)" % (height, depth)
	self.__stretch_height = height
	self.__stretch_depth  = depth
	try:
	    self.__parts = _stretchy_parenthesis[self.content]
	except KeyError:
	    self.__parts = None
	    warnings.warn("Cannot stretch '%s'" %
			  ",".join([hex(ord(c)) for c in self.content]))

    def setHStretch(self, width):
	self.__stretch_width = width

    def _draw_non_stretchy(self):
	pl = self.plotter
	pl.setfont(self.font_family, self.font_style, self.font_size)
	pl.moveto(0, 0)
	pl.label(self.subst_content, self.__layout_cache)

    def _close_gap(self, gap_start, gap_end, bar):
	if gap_start >= gap_end:
	    #print("Warning: '%s': gap_start = %f; gap_end = %f" %
	    #  (self.content, gap_start, gap_end))
	    return
	pl = self.plotter
	_, width, height, _ = pl.labelmetrics(bar)
	if height <= 0: return # height == 0 produces an infinite loop!
	y = gap_start
	while y < gap_end:
	    pl.moveto(0, y)
	    if y + height > gap_end:
		pl.savestate()
		pl.setcliprect(-width, y, width*2, gap_end)
		pl.label(bar)
		pl.restorestate()
		# debugging
		#pl.linewidth(self.font_size*0.02)
		#pl.moveto(-width, y)
		#pl.lineto(width*2, y)
		#pl.lineto(width*2, y*.9)
		#pl.moveto(-width, gap_end)
		#pl.lineto(width*2, gap_end)
		#pl.lineto(width*2, gap_end*1.1)
	    else:
		pl.label(bar)
	    y += height

    def _draw_stretchy(self):
	pl = self.plotter
	pl.setfont(self.__stretchy_font_family, self.__stretchy_font_style,
		   self.__stretched_font_size)

	# Lower part
	_, _, lower_gap_start, _ = pl.labelmetrics(self.__parts.lower)
	pl.moveto(0, 0)
	pl.label(self.__parts.lower)

	# Upper part
	_, _, height, _ = pl.labelmetrics(self.__parts.upper)
	upper_gap_end = self.height - height
	pl.moveto(0, upper_gap_end)
	pl.label(self.__parts.upper)

	if self.__parts.middle is None:
	    self._close_gap(lower_gap_start, upper_gap_end,
			    self.__parts.bar)
	else:
	    # Middle part
	    _, _, height, _ = pl.labelmetrics(self.__parts.middle)
	    lower_gap_end = self.__stretch_depth - height/2
	    upper_gap_start = self.__stretch_depth + height/2
	    pl.moveto(0, lower_gap_end)
	    pl.label(self.__parts.middle)
	    self._close_gap(lower_gap_start, lower_gap_end,
			    self.__parts.bar)
	    self._close_gap(upper_gap_start, upper_gap_end,
			    self.__parts.bar)
	    
    def draw(self):
	if (self.content == unichr(0x2062) or
	    self.content == unichr(0x2061)):
	    return
	if self.__stretch_width is not None:
	    self._draw_hstretchy()
	elif self.__parts is not None:
	    self._draw_stretchy()
	else:
	    self._draw_non_stretchy()

    def _update_hstretchy(self):
	## This is called "Lazy Horizontal Stretching (TM)": just
	## scale the font to make the label as wide as needed :P
	pl = self.plotter
	pl.setfont(self.font_family, self.font_style, self.font_size)
	_, width, height, axis = pl.labelmetrics(self.subst_content)
	scaling = self.__stretch_width/width

	self.__stretched_font_size = self.font_size*scaling
	pl.setfont(self.font_family, self.font_style, self.__stretched_font_size)
	_, self.width, self.height, self.axis = pl.labelmetrics(self.subst_content)

    def _draw_hstretchy(self):
	pl = self.plotter
	pl.setfont(self.font_family, self.font_style, self.__stretched_font_size)
	pl.moveto(0, 0)
	pl.label(self.subst_content, self.__layout_cache)
	

    def __str__(self):
	return str(self.__class__) + "('"+self.content+"')"

class MText(MToken):
    def __init__(self, plotter, content):
	MToken.__init__(self, plotter, content)
	self.font_family = MTEXT_FONT[0]
	self.font_style  = MTEXT_FONT[1]

class MError(MToken):
    def __init__(self, plotter, content):
	MToken.__init__(self, plotter, content)
	self.font_family = MERROR_FONT[0]
	self.font_style  = MERROR_FONT[1]

class MOperator(MToken):
    def __init__(self, plotter, content):
	MToken.__init__(self, plotter, content)
	self.__original_content = content
	self.font_family = MO_FONT_REGULAR[0]
	self.font_style  = MO_FONT_REGULAR[1]

    def update(self):
	form = self.getAttribute("form", recursive=0, default="infix").str
	try:
	    attrs = opdict.lookup(self.__original_content, form)
	    #print "found opdict entry for ", self.__original_content, ":"
	    for key, value in attrs.items():
		#print "%s => %s" % (key, value)
		self.setAttributeWeak(key, value)
	except KeyError:
	    warnings.warn("Couldn't find operator '%s' in operator dictionary" % (self.content, ))
	#if self.content == '-':
	#    self.content = unichr(0x2212)
	MToken.update(self)

    def embellished_p(self):
	return self


class MNumber(MToken):
    def __init__(self, plotter, content):
	MToken.__init__(self, plotter, content)
	self.font_family = MN_FONT[0]
	self.font_style  = MN_FONT[1]

class MIdentifier(MToken):
    def __init__(self, plotter, content):
	MToken.__init__(self, plotter, content)
	if len(content) > 1:
	    self.font_family = MI_FONT_REGULAR[0]
	    self.font_style  = MI_FONT_REGULAR[1]
	else:
	    self.font_family = MI_FONT_ITALIC[0]
	    self.font_style  = MI_FONT_ITALIC[1]

# __all__ = (
#     'MText',
#     'MOperator',
#     'MNumber',
#     'MIdentifier')

xml_mapping['mtext']  = MText
xml_mapping['merror'] = MError
xml_mapping['mo']     = MOperator
xml_mapping['mi']     = MIdentifier
xml_mapping['mn']     = MNumber

