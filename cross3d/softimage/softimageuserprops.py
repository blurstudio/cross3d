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
from blur3d import api
import re
#from blurdev.enum import enum

class SoftimageUserProps(AbstractUserProps):
	#dataTypes = enum('ClusterProperty', 'CustomProperty', 'Property', 'UserDataBlob', 'UserDataMap')
	def __init__(self, nativePointer):
		super(SoftimageUserProps, self).__init__(nativePointer)
		self._nativePointer = nativePointer
	
	def __delitem__(self, key):
		prop = self._nativePointer.Properties(key)
		if not prop:
			raise KeyError('%s is not a property' % key)
		scene = api.Scene()
		obj = scene.findObject(prop.FullName)
		scene.removeObjects([obj])
	
	def __getitem__(self, key):
		return self.unescapeValue(self._nativePointer.Properties(key).Value)
		#return self.lookupProps()[key]
	
	def __setitem__(self, key, value):
		prop = self._nativePointer.Properties(key)
		if isinstance(value, (list, dict, tuple)):
			value = unicode(value)
		if not prop:
			prop = self._nativePointer.AddProperty( 'UserDataBlob', False, key)
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
	
	@staticmethod
	def escapeValue(string):
		"""
			\remarks	replaces any unstorable characters in value with their html codes
			\return		<str>
		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		#return string.replace('\r\n', '&#13;&#10;').replace('\n', '&#10;').replace('\r', '&#13;')		
		return string
	
	@staticmethod
	def unescapeValue(string):
		"""
			\remarks	replaces any html codes with their associated unstorable characters
						does not pickle/unpickle data.
			\return		<float>||<int>||<list>||<dict>||<tuple>||<unicode>
		"""
		string = unicode(string)
		string, type = SoftimageUserProps._decodeString(string)
		if type == float:
			return float(string)
		elif type == int:
			return int(string)
		elif type in (list, dict, tuple):
			try:
				return eval(string)
			except:
				return string
		return string
		#return string.replace('&#13;&#10;', '\r\n').replace('&#10;', '\n').replace('&#13;', '\r')
	
	@staticmethod
	def _decodeString(string):
		if re.search('\[.+\]', string):
			return string, list
		if re.search('{.+}', string):
			return string, dict
		if re.search('\(.+\)', string):
			return string, tuple
		if string.find('.') != -1:
			try:
				float(string)
				return string, float
			except:
				pass
		try:
			int(string)
			return string, int
		except:
			pass
		return string, None

# register the symbol
api.registerSymbol( 'UserProps', SoftimageUserProps )