import maya.OpenMaya as om
import maya.cmds as cmds
from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps, AbstractFileProps
from blur3d import api

class MayaUserProps(AbstractUserProps):
	def __contains__(self, key):
		return api.SceneWrapper._hasAttribute(self._nativePointer, key)
	
	def __getitem__(self, key):
		return self.unescapeValue(api.SceneWrapper._getAttribute(self._nativePointer, key))
	
	def __setitem__(self, key, value):
		# Note: self.escapeKey(key) will be called when we create the attribute, so there is no
		# reason to call it twice.
		value = self.escapeValue(value)
		if not api.SceneWrapper._hasAttribute(self._nativePointer, key):
			key, shortName = api.SceneWrapper._createAttribute(self._nativePointer, key, 
					dataType=om.MFnData.kString)
		# Set the current attribute
		api.SceneWrapper._setAttribute(self._nativePointer, key, value)
		# Notify listening slots about the change
		self.emitChange()
	
	def keys(self):
		# Only show user defined keys
		out = cmds.listAttr(api.SceneWrapper._MObjName(self._nativePointer), userDefined=True)
		if out:
			return out
		return []
		# Note: I was unable to find a way to identify userDefined keys in the following method
		# so I used the maya.cmds method. If possible this finish this method and replace the 
		# above code.
		#depNode = om.MFnDependencyNode(mObj)
		#total = depNode.attributeCount()
		#count = 0
		#while count < total:
		#	attr = depNode.attribute(count)
		#	plug = om.MPlug(mObj, attr)
		#	count += 1
		#	print count, attr.apiTypeStr(), plug.name()
	
	def get(self, key, default=None):
		if key in self.keys():
			return self[key]
		return default
	
	def has_key(self, key):
		return self.__contains__(key)
	
	def lookupProps(self):
		ret = {}
		for key in self.keys():
			ret.update({key: self[key]})
		return ret
	
	def pop(self, key, default=None):
		if not key in self.keys():
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
	
	@staticmethod
	def escapeKey(string):
		""" Replaces any unstorable characters in key with their html codes """
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return api.SceneWrapper._normalizeAttributeName(string)

class MayaFileProps(MayaUserProps):
	pass

# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', MayaUserProps )
api.registerSymbol( 'FileProps', MayaFileProps )