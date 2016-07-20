##
#	\namespace	cross3d.SoftimageUserProps
#
#	\remarks	The cross3d.SoftimageUserProps handles storing and retreving custom
#				properties from objects
#	
#	\author		mikeh 
#	\author		Blur Studio
#	\date		05/26/11
#

import re
import json
import cross3d
from PyQt4.QtCore import QString
from win32com.client import constants
from cross3d.abstract.abstractuserprops 	import AbstractUserProps, AbstractFileProps

class SoftimageUserProps(AbstractUserProps):
	#dataTypes = enum('ClusterProperty', 'CustomProperty', 'Property', 'UserDataBlob', 'UserDataMap')
	def __init__(self, nativePointer):
		super(SoftimageUserProps, self).__init__(nativePointer)
		self._nativePointer = nativePointer
	
	def __delitem__(self, key):
		prop = self._nativePointer.Properties(key)
		if not prop:
			raise KeyError('%s is not a property' % key)
		scene = cross3d.Scene()
		obj = scene.findObject(prop.FullName)
		scene.removeObjects([obj])
	
	def __getitem__(self, key):
		return self.unescapeValue(self._nativePointer.Properties(key).Value)
	
	def __setitem__(self, key, value):
		prop = self._nativePointer.Properties(key)
		if type(value) == tuple:
			# json.dumps encodes tuple's as lists
			value = unicode(value)
		else:
			value = json.dumps(value)
		if not prop:
			prop = self._nativePointer.AddProperty('UserDataBlob', False, key)
			prop.SetCapabilityFlag(constants.siNotInspectable, True)
		if not value:
			# For some reason xsi does not let you set a UserDataBlob to a empty string, you have to use the clear method.
			prop.clear()
		else:
			prop.Value = value
		self.emitChange(key)

	def clear(self):
		"""
			\remarks	remove all userProps from the object, Use with caution, it will remove any UserDataBlob objects.
		"""
		for item in self.lookupProps().keys():
			del self[item]

	def pop(self, key, default = None):
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
		baseprops = self._nativePointer.Properties.Filter( 'UserDataBlob' )
		props = {}
		for prop in baseprops:
			key = prop.Name
			value = prop.Value
			props[ key ] = self.unescapeValue( value )
		return props
	
	def setHidden(self, key, state):
		"""
		Hide the mecinism that stores user props in software that supports it.
		:param key: The key used to access the user prop
		:param state: If the item is hidden or shown
		"""
		prop = self._nativePointer.Properties(key)
		if not prop:
			raise KeyError('%s is not a property' % key)
		prop.SetCapabilityFlag(constants.siNotInspectable, state)
		return True
	
	@staticmethod
	def escapeValue(string):
		"""
			\remarks	replaces any unstorable characters in value with their html codes
			\return		<str>
		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)		
		return string

class SoftimageFileProps(SoftimageUserProps):
	def __init__(self, nativePointer):
		super(SoftimageFileProps, self).__init__( cross3d.Scene().rootObject().nativePointer())

# register the symbol
cross3d.registerSymbol('UserProps', SoftimageUserProps)
cross3d.registerSymbol('FileProps', SoftimageFileProps)
