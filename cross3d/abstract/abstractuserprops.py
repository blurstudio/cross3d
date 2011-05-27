##
#	\namespace	blur3d.api.UserProps
#
#	\remarks	The blur3d.api.UserProps package creates an abstract wrapper from a 3d system
#				to use storing and retreiving custom user props
#	
#	\author		mike@blur.com
#	\author		Blur Studio
#	\date		05/26/11
#
#|# get object
#|import blur3d
#|scene = blur3d.api.Scene()
#|selection = scene.selection()
#|object = selection[0]
#|# set blurTags
#|tags = object.blurTags()
#|tags.update(type='Character', entity='Dalton', usage='Shaded', location='Right', 
#|render='Rndr', cache='tmc', variation = 3)
#|tags['subdivision'] = 4
#|# set custom properties
#|prop = object.userProps()
#|prop['tagA'] = '36'
#|prop['customProp'] = 'My custom property'

from PyQt4.QtCore import QString

class AbstractUserProps(dict):
	def __init__(self, nativePointer):
		dict.__init__(self)
		self._nativePointer = nativePointer
	
	def __contains__(self, key):
		return key in self.lookupProps()
	
	def __getitem__(self, key):
		key = self.typeCheck(key)
		return dict.__getitem__(self, key)
	
	def __setitem__(self, key, value):
		key = self.typeCheck(key)
		value = self.typeCheck(value)
		dict.__setitem__(self, key, value)
	
	def __str__(self):
		return str(self.lookupProps())
	
#	def __repr__(self):
#		return 'UserProps(%s)' % self._nativePointer
	
	def clear(self):
		self.lookupProps().clear()
	
	def copy(self):
		return self.lookupProps().copy()
	
	def keys(self):
		return self.lookupProps().keys()
	
	def items(self):
		return self.lookupProps().items()
	
	def iteritems(self):
		return self.lookupProps().iteritems()
	
	def iterkeys(self):
		return self.lookupProps().iterkeys()
	
	def itervalues(self):
		return self.lookupProps().itervalues()
	
	def has_key(self, key):
		return self.lookupProps().has_key(key)
	
	def get(self, key, default = None):
		return self.lookupProps().get(key, default)
	
	def lookupProps(self):
		"""
			\remarks	this is the workhorse method for the class, it is responsible for providing the dictionary of key value pares used for 
						most of the class. If it is unabstracted it will return a empty dictionary
			\return		<dict>
		"""
		return {}
	
	def pop(self, key, default = None):
		return self.lookupProps().pop(key, default)
	
	def popitem(self):
		return self.lookupProps().popitem()
	
	def setdefault(self, key, default = None):
		return self.lookupProps().setdefault(key, default)
	
	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v
	
	def values(self):
		return self.lookupProps().values()
	
	@staticmethod
	def escapeKey(string):
		"""
			\remarks	replaces any unstorable characters in key with their html codes
			\return		<str>
		"""
		return string.replace(' ', '&#32;').replace('\n', '&#10;').replace('\r', '&#13;')
	
	@staticmethod
	def escapeValue(string):
		"""
			\remarks	replaces any unstorable characters in value with their html codes
			\return		<str>
		"""
		return string.replace('\r\n', '&#13;&#10;').replace('\n', '&#10;').replace('\r', '&#13;')
	
	@staticmethod
	def typeCheck(string):
		"""
			\remarks	Returns the string. Raises a TypeError if the input is not a string or unicode. If the input is a QString it converts it to unicode.
			\return		<str>
		"""
		if not isinstance(string, (str, unicode)):
			if isinstance(string, QString):
				return unicode(string)
			else:
				# raise type error
				raise TypeError(('UserProps requires a <str> or <unicode> you provided <%s>' % string.__class__.__name__))
		return string
				
	
	@staticmethod
	def unescapeKey(string):
		"""
			\remarks	replaces any html codes with their associated unstorable characters
			\return		<str>
		"""
		return string.replace('&#32;', ' ').replace('&#10;', '\n').replace('&#13;', '\r')
	
	@staticmethod
	def unescapeValue(string):
		"""
			\remarks	replaces any html codes with their associated unstorable characters
			\return		<str>
		"""
		return string.replace('&#13;&#10;', '\r\n').replace('&#10;', '\n').replace('&#13;', '\r')


# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', AbstractUserProps, ifNotFound = True )