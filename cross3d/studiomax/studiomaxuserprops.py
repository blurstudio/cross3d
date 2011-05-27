##
#	\namespace	blur3d.api.StudiomaxUserProps
#
#	\remarks	The blur3d.api.StudiomaxUserProps handles storing and retreving custom
#				properties from objects
#	
#	\author		mikeh@blur.com
#	\author		Blur Studio
#	\date		05/23/11
#

from Py3dsMax import mxs
from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps

class StudiomaxUserProps(AbstractUserProps):
	def __init__(self, nativePointer):
		super(StudiomaxUserProps, self).__init__(nativePointer)
		self._nativePointer = nativePointer
	
	def __delitem__(self, key):
		"""
			\remarks	There is no build in way to remove keys from userProp's so we create a copy of our userProps dictionary
						clear userProps on the object, remove the item we want to remove and restore the remaining data to the object.
		"""
		key = self.typeCheck(key)
		data = self.lookupProps()
		if key in data:
			self.clear()
			data.pop(key)
			self.update(data)
	
	def __getitem__(self, key):
		key = self.typeCheck(key)
		return self.unescapeValue(mxs.getUserProp(self._nativePointer, self.escapeKey(key)))
	
	def __setitem__(self, key, value):
		key = self.typeCheck(key)
		value = self.typeCheck(value)
		mxs.setUserProp(self._nativePointer, self.escapeKey(key), self.escapeValue(value))

	def clear(self):
		"""
			\remarks	remove all userProps from the object
		"""
		mxs.setUserPropBuffer(self._nativePointer, '')
	
	def pop(self, key, default = None):
		key = self.typeCheck(key)
		if not key in self.lookupProps():
			if default:
				return default
			raise KeyError(self.unescapeKey(key))
		out = self[key]
		del self[key]
		return out
	
	def popitem(self):
		data = self.lookupProps()
		if not data:
			raise KeyError('popitem(): dictionary is empty')
		item = data.popitem()
		del self[item[0]]
		return item

	def lookupProps(self):
		string = mxs.getUserPropBuffer(self._nativePointer)
		keyValues = string.split('\r\n')
		props = {}
		for kv in keyValues:
			split = kv.split(' = ', 1)
			if not len(split) == 2:
				split = kv.split('=', 1)
				if not len(split) == 2:
					split = kv.split(' ', 1)
					if not len(split) == 2:
						continue
			props[self.unescapeKey(split[0])] = self.unescapeValue(split[1])
		return props

# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', StudiomaxUserProps )