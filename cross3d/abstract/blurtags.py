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

class BlurTags(dict):
	def __init__(self, object):
		dict.__init__(self)
		self._object = object
	
	def __contains__(self, key):
		return key in self.lookupProps()
	
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
			return eval(props['BlurTags'])
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

# register the symbol
from blur3d import api
api.registerSymbol( 'BlurTags', BlurTags, ifNotFound = True )