import opdict_data
import entities


opdict = {}

import os
def _lookup_entity(content):
    if content.startswith('&') and content.endswith(';'):
	return entities.map[content[1:-1]]
    else:
	return content

for line in opdict_data.data.split('\n'):
    tokens = line.split()
    if not tokens: continue
    try:
	content = _lookup_entity(tokens[0][1:-1])
    except KeyError:
	continue
    attrs = {}
    for token in tokens[1:]:
	name, value = token.split('=')
	attrs[name] = value[1:-1] # removes quotes
    form = intern(attrs['form'])
    del attrs['form']
    if opdict.has_key(content):
	opdict[content][form] = attrs
    else:
	opdict[content] = {form: attrs}

_default_attributes = {
    "fence":         "false",
    "separator":     "false",
    "lspace":        "thickmathspace",
    "rspace":        "thickmathspace",
    "stretchy":      "false",
    "symmetric":     "true",
    "maxsize":       "infinity",
    "minsize":       "1",
    "largeop":       "false",
    "movablelimits": "false",
    "accent":        "false"
    }

def lookup(content, form):
    try:
	entry = opdict[content]
    except KeyError:
	return _default_attributes
    try:
	return entry[form]
    except KeyError:
	try:
	    return entry['infix']
	except KeyError:
	    try:
		return entry['postfix']
	    except KeyError:
		try:
		    return entry['prefix']
		except KeyError:
		    return _default_attributes

