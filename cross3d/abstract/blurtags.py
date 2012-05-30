##
#	\namespace	blur3d.api.BlurTags
#
#	\remarks	The blur3d.api.BlurTags retreives the BlurTags property using UserProps it then converts the
#				string into a python dictionary
#	
#	\author		mikeh@blur.com
#	\author		Blur Studio
#	\date		05/23/11
#

from blur3d.naming import Name

class BlurTags(dict):
	def __init__(self, object):
		dict.__init__(self)
		self._object = object
	
	def __contains__(self, key):
		return key in self.lookupProps()
	
	def __delitem__(self, key):
		props = self.lookupProps()
		del props[key]
		self._object.userProps()['BlurTags'] = str(props)
	
	def __getitem__(self, key):
		return self.lookupProps().__getitem__(key)
	
	def __setitem__(self, key, value):
		props = self.lookupProps()
		props[key] = value
		self._object.userProps()['BlurTags'] = str(props)
	
	def __str__(self):
		return str(self.lookupProps())
	
#	def __repr__(self):
#		return 'BlurTags(%s)' % self._nativePointer
	
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
						most of the class. If the tag exists it returns an evaluated version of its contents
			\return		<dict>
		"""
		props = self._object.userProps()
		if 'BlurTags' in props:
			return props['BlurTags']
		return {}
	
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
	
	def setdefault(self, key, default = None):
		return self.lookupProps().setdefault(key, default)
		
	
	def toString(self, prefix = '', seperator = ':', postfix = ' '):
		out = ''
		for key, value in self.lookupProps().items():
			line = prefix + key + seperator + unicode(value) + postfix
			out += line
		return out
		
	
	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v
	
	def updateTagsFromName( self, format = 'Legacy::Object' ):
		name = Name( self._object.name(), format )
		for element in name.elements():
			key = element.objectName()
			text = element.text()
			if text == 'X':
				if key in self:
					del self[ key ]
			else:
				self.update({key:text})
		
	
	def values(self):
		return self.lookupProps().values()
		

# register the symbol
from blur3d import api
api.registerSymbol( 'BlurTags', BlurTags, ifNotFound = True )