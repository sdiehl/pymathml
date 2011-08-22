import weakref

class EventSource(object):
    """A GObject-like signal framework"""

    def __init__(self):
        self.__connections = {}

    def connect(self, name, handler, data=None):
	try:
	    l = self.__connections[name]
	except KeyError:
	    l = []
	    self.__connections[name] = l
	item = weakref.ref(handlerobject)
	l.append((handler, data))

    def emit(self, name, args):
	try:
	    l = self.__connections[name]
	except KeyError:
	    return
	for handler, data in l:
	    _handler = handler()
	    # if weak reference no longer exists, remove this entry
	    if _handler is None:
		l.remove((handler, data))
		continue
	    _args = [self] + args
	    if data is not None:
		_args.append(data)
	    # invoke handler
	    _handler(*_args)


