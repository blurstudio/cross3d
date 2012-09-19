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
#|prop['tagA'] = 36
#|prop['customProp'] = 'My custom property'

import blur3d
from blur3d import api


dispatchObject = blur3d.api.dispatch.dispatchObject


class AbstractUserProps(dict):
	"""
	The blur3d.api.UserProps package creates an abstract wrapper from a 
	3d system to use storing and retreiving custom user props
	"""

	def __init__(self, nativePointer):
		dict.__init__(self)
		self._nativePointer = nativePointer

	def __contains__(self, key):
		return key in self.lookupProps()

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		self.emitChange()

	def __str__(self):
		return str(self.lookupProps())

	def clear(self):
		self.lookupProps().clear()

	def copy(self):
		return self.lookupProps().copy()

	def emitChange(self, key):
		if key == 'BlurTags':
			dispatchObject('blurTagChanged', self._nativePointer)
		else:
			dispatchObject('customPropChanged', self._nativePointer)

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

	def get(self, key, default=None):
		return self.lookupProps().get(key, default)

	def lookupProps(self):
		"""
		This is the workhorse method for the class, it is responsible for 
		providing the dictionary of key value pares used for most of the 
		class. If it is unabstracted it will return a empty dictionary
		
		:return: dict
		
		"""
		return {}

	def pop(self, key, default=None):
		return self.lookupProps().pop(key, default)

	def popitem(self):
		return self.lookupProps().popitem()

	def setdefault(self, key, default=None):
		return self.lookupProps().setdefault(key, default)

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

	def values(self):
		return self.lookupProps().values()

	@staticmethod
	def escapeKey(string):
		"""
		Replaces any unstorable characters in key with their html codes
		
		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace(' ', '&#32;').replace('\n', '&#10;').replace('\r', '&#13;')

	@staticmethod
	def escapeValue(string):
		"""
		Replaces any unstorable characters in value with their html codes

		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace('\r\n', '&#13;&#10;').replace('\n', '&#10;').replace('\r', '&#13;')

	@staticmethod
	def unescapeKey(string):
		"""
		Replaces any html codes with their associated unstorable characters

		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace('&#32;', ' ').replace('&#10;', '\n').replace('&#13;', '\r')

	@staticmethod
	def unescapeValue(string):
		"""
		Replaces any html codes with their associated unstorable characters

		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace('&#13;&#10;', '\r\n').replace('&#10;', '\n').replace('&#13;', '\r')


# register the symbol
api.registerSymbol('UserProps', AbstractUserProps, ifNotFound=True)
