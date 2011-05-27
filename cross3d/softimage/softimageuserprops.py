##
#	\namespace	blur3d.api.SoftimageUserProps
#
#	\remarks	The blur3d.api.SoftimageUserProps handles storing and retreving custom
#				properties from objects
#	
#	\author		mikeh@blur.com
#	\author		Blur Studio
#	\date		05/26/11
#

#from PySoftimage import xsi
from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps
from blur3d.api import Scene
from blurdev.enum import enum

class SoftimageUserProps(AbstractUserProps):
	#dataTypes = enum('ClusterProperty', 'CustomProperty', 'Property', 'UserDataBlob', 'UserDataMap')
	def __init__(self, nativePointer):
		super(SoftimageUserProps, self).__init__(nativePointer)
		self._nativePointer = nativePointer
	
	def __delitem__(self, key):
		key = self.typeCheck(key)
		prop = self._nativePointer.Properties(key)
		if not prop:
			raise KeyError('%s is not a property' % key)
		scene = Scene()
		obj = scene.findObject(prop.FullName)
		scene.removeObjects([obj])
	
	def __getitem__(self, key):
		key = self.typeCheck(key)
		return self._nativePointer.Properties(key).Value
	
	def __setitem__(self, key, value):
		key = self.typeCheck(key)
		value = self.typeCheck(value)
		prop = self._nativePointer.Properties(key)
		if not prop:
			prop = self._nativePointer.AddProperty( 'UserDataBlob', False, key)
		prop.Value = value

	def clear(self):
		"""
			\remarks	remove all userProps from the object, Use with caution, it will remove any UserDataBlob objects.
		"""
		for item in self.lookupProps().keys():
			del self[item]

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
		baseprops = self._nativePointer.Properties
		props = {}
		for prop in baseprops:
			if prop.Type in ("UserDataBlob"):
				key = prop.Name
				value = prop.Value
				props[key] = value
		return props

# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', SoftimageUserProps )