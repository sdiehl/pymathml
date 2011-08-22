from __future__ import generators
from element import *
import warnings
from mrow import MRow

'''
An implemenation of <mtable> <mtr> and <mtd>.
It works, but is incomplete, and ignores a lot of attributes.

TODO:
	- row and column lines
	- frame
	- table alignment (hardcoded to "center")
	- cell vertical alignment (hardcoded to "center")
	- alignment markers
	- etc.
'''

class MTD(Element):
    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	for child in children:
	    self.addChild(child)
	self.strategy = MRow.Strategy()

    def update(self):
	self.strategy.modify_children(self.children)
	for child in self: child.update()
	self.width, self.height, self.axis = self.strategy.layout(self.children)


class MTR(Element):
    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	for child in children:
	    assert isinstance(child, MTD)
	    self.addChild(child)

class MTable(Element):

    class Column:
	ALIGN_LEFT   = 1
	ALIGN_CENTER = 2
	ALIGN_RIGHT  = 3
	__slots__ = ('left', 'right', 'width')

    class Row:
	__slots__ = ('top', 'bottom', 'height')

    class Cell:
	__slots__ = ('elem', 'row', 'col', 'colspan', 'rowspan', 'columnalign')

    class Table:
	def __init__(self, rows, cols):
	    self.rows = []
	    for i in range(rows):
		elems = []
		for j in range(cols):
		    elems.append(None)
		self.rows.append(elems)
	def set(self, row, col, cell):
	    self.rows[row][col] = cell
	def get(self, row, col):
	    return self.rows[row][col]
	def __iter__(self):
	    for row in self.rows:
		for cell in row:
		    if cell is None: continue
		    yield cell
    # ---
    def __init__(self, plotter, children):
	Element.__init__(self, plotter)
	for child in children:
	    assert isinstance(child, MTR)
	    self.addChild(child)

    def update(self):
	rows  = []
	cols  = []

	rowspacing = self.getAttribute("rowspacing", recursive=False, default="1ex").asLength()
	colspacing = self.getAttribute("colspacing", recursive=False, default="0.8em").asLength()

	# compute table dimmensions (number of rows and columns)
	numcols = 0
	numrows = 0
	for mrow in self.children:
	    x = 0
	    for mdata in mrow.children:
		# get size of table elements once
		mdata.update()
		# get columnspan
		colspan = mdata.getAttribute('columnspan', recursive=False, default=1).asInt()
		x += colspan
	    numcols = max(numcols, x)
	    numrows += 1
	cells = self.Table(numrows, numcols)

	# default column align
	attr = self.getAttribute("columnalign", recursive=False, default="center").str
	if attr == "left":
	    columnalign_def = self.Column.ALIGN_LEFT
	elif attr == "right":
	    columnalign_def = self.Column.ALIGN_RIGHT
	elif attr == "center":
	    columnalign_def = self.Column.ALIGN_CENTER
	else:
	    raise ValueError("Invalid columnalign '" + attr + "'")
	y = 0
	for mrow in self.children:
	    x = 0
	    for mdata in mrow.children:
		# skip occupied cells
		while cells.get(y, x) is not None:
		    x += 1
		    if x > numcols:
			x = 0
			y += 1
			assert y < numrows
		rowspan = mdata.getAttribute('rowspan', recursive=False, default=1).int
		colspan = mdata.getAttribute('columnspan', recursive=False, default=1).int
		
		cell = self.Cell()
		cell.elem    = mdata;
		cell.row     = y;
		cell.col     = x;
		cell.rowspan = rowspan;
		cell.colspan = colspan;
		# get columnalign
		attr = mdata.getAttribute("columnalign", recursive=False)
		if attr is None:
		    cell.columnalign = columnalign_def
		else:
		    attr = attr.str
		    if attr == "left":
			cell.columnalign = self.Column.ALIGN_LEFT
		    elif attr == "right":
			cell.columnalign = self.Column.ALIGN_RIGHT
		    elif attr == "center":
			cell.columnalign = self.Column.ALIGN_CENTER
		    else:
			raise ValueError("Invalid columnalign '" + attr + "'")
		# fill the table with cells
		for y1 in range(y, y + rowspan):
		    for x1 in range(x, x + colspan):
			cells.set(y1, x1, cell)
		x += 1
	    y += 1
	# ---
	for i in range(numrows):
	    row = self.Row()
	    row.height = 0
	    rows.append(row)
	for j in range(numcols):
	    col = self.Column()
	    col.width = 0
	    cols.append(col)
	for span in range(1, numcols + 1):
	    for cell in cells:
		# compute column widths    
		if cell.colspan == span:
		    if span == 1:
			cols[cell.col].width = max(cols[cell.col].width, cell.elem.width)
		    else:
			size = 0
			for x in range(cell.col, cell.col + cell.colspan):
			    size += cols[x].width
			    if size < cell.elem.width:
				remaining = (cell.elem.width - size) / cell.colspan
			for x in range(cell.col, cell.col + cell.colspan):
			    cols[x].width += remaining
		# compute row heights
		if cell.rowspan == span:
		    if span == 1:
			rows[cell.row].height = max(rows[cell.row].height, cell.elem.height)
		    else:
			size = 0
			for x in range(cell.row, cell.row + cell.rowspan):
			    size += rows[x].height
			    if size < cell.elem.height:
				remaining = (cell.elem.height - size) / cell.rowspan
			for x in range(cell.row, cell.row + cell.rowspan):
			    rows[x].height += remaining
	# get column positions and total table width
	offset = 0
	for col in cols:
	    col.left   = offset
	    offset    += col.width
	    col.right  = offset;
	    offset    += colspacing
	self.width = offset - colspacing
	# get row positions and total table height
	offset = 0
	for row in rows:
	    row.top     = offset
	    offset     -= row.height
	    row.bottom  = offset;
	    offset     -= rowspacing
	self.height = -(offset + rowspacing)
	# shift all rows up by the amount 'self.height'
	for row in rows:
	    row.top    += self.height
	    row.bottom += self.height
	# finally, layout the individual table elements
	for cell in cells:
	    # cell boundaries
	    cell_y2 = rows[cell.row].top
	    cell_y1 = rows[cell.row + cell.rowspan - 1].bottom
	    cell_x1 = cols[cell.col].left
	    cell_x2 = cols[cell.col + cell.colspan - 1].right
	    # align element within cell boundaries
	    if cell.columnalign == self.Column.ALIGN_CENTER:
		cell.elem.x0 = (cell_x1 + cell_x2)/2 - cell.elem.width/2
	    elif cell.columnalign == self.Column.ALIGN_LEFT:
		cell.elem.x0 = cell_x1
	    elif cell.columnalign == self.Column.ALIGN_RIGHT:
		cell.elem.x0 = cell_x2 - cell.elem.width
	    else:
		assert 0, "invalid column alignment!"
	    # FIXME: rowalign not implemented; hardcoded to 'center' for now
	    cell.elem.y0 = (cell_y1 + cell_y2)/2 - cell.elem.height/2
	# and we're done!


# ---
xml_mapping['mtable'] = MTable
xml_mapping['mtd']    = MTD
xml_mapping['mtr']    = MTR

