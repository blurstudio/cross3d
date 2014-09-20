from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps, AbstractFileProps
from blur3d import api

class MayaUserProps(AbstractUserProps):
	def __contains__(self, key):
		return api.SceneWrapper._hasAttribute(self._nativePointer, key)
	
	def __getitem__(self, key):
		return self.unescapeValue(api.SceneWrapper._getAttribute(self._nativePointer, key))
	
	def __setitem__(self, key, value):
		key = self.escapeKey(key)
		mxs.setUserProp(self._nativePointer, self.escapeKey(key), self.escapeValue(value))
		self.emitChange()
	
	def has_key(self, key):
		return self.__contains__(key)

class MayaFileProps(MayaUserProps):
	pass

# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', MayaUserProps )
api.registerSymbol( 'FileProps', MayaFileProps )