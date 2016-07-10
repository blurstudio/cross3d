import maya.OpenMaya as om
import maya.cmds as cmds
import cross3d
from cross3d.abstract.abstractuserprops import AbstractUserProps, AbstractFileProps

class MayaUserProps(AbstractUserProps):
	# MCH 09/30/14 Dev Note:  If it is possible to store metadata without changing selection
	# in the way used in MayaFileProps, This class should be re-implemented to store data that
	# way. Currently I can't figure out how to do that without wrighting a plugin, so MayaUserProps
	# stores its data as OpenMaya.MObject attributes.
	def __contains__(self, key):
		return cross3d.SceneWrapper._hasAttribute(self._nativePointer, key)
	
	def __delitem__(self, key):
		if not key in self:
			raise KeyError('{} is not stored in UserProps'.format(key))
		cmds.deleteAttr(cross3d.SceneWrapper._mObjName(self._nativePointer), attribute=key)
	
	def __getitem__(self, key):
		if not key in self:
			raise KeyError('{} is not stored in UserProps'.format(key))
		node = cross3d.SceneWrapper._mObjName(self._nativePointer)

		# TODO MIKE: I had to do a try except here for the character native object that already has native custom attributes.
		# Maybe there is a better way to handle that.
		try:
			return self.unescapeValue(cmds.getAttr('{node}.{attr}'.format(node=node, attr=key)))
		except RuntimeError:
			return None

	
	def __setitem__(self, key, value):
		# Note: self.escapeKey(key) will be called when we create the attribute, so there is no
		# reason to call it twice.
		value = self.escapeValue(value)
		if not cross3d.SceneWrapper._hasAttribute(self._nativePointer, key):
			key, shortName = cross3d.SceneWrapper._createAttribute(self._nativePointer, key, 
					dataType=om.MFnData.kString)
		# Set the current attribute
		cross3d.SceneWrapper._setAttribute(self._nativePointer, key, value)
		# Notify listening slots about the change
		self.emitChange()
	
	def keys(self):

		# TODO MIKE: I had to do a try except here for the the object called "|groundPlane_transform".
		# It's apparently always in the scene and error with that line.
		try:
			keys = cmds.listAttr(cross3d.SceneWrapper._mObjName(self._nativePointer), userDefined=True)
			if keys:
				return keys
		except ValueError:
			pass
		return []
		
		# http://forums.cgsociety.org/showthread.php?t=888612
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
		return cross3d.SceneWrapper._normalizeAttributeName(string)

class MayaFileProps(MayaUserProps):
	def _hasStruct(self):
		return cmds.dataStructure(name=self._structureName, query=True)
	
	def _hasMetaDataChannel(self):
		return cmds.hasMetadata(scene=True, channelName=self._channelName, asList=True)
	
	def __contains__(self, key):
		# if the structure is not defined the key is not stored and hasMetadata will error out
		if not self._hasStruct():
			return False
		return key in cmds.hasMetadata(scene=True, streamName=self._cross3dStream, asList=True)
	
	def __delitem__(self, key):
		if not key in self:
			raise KeyError('{} is not stored in FileProps'.format(key))
		cmds.editMetadata(streamName=self._cross3dStream, index=key, scene=True, remove=True)
	
	def __getitem__(self, key):
		if not key in self:
			raise KeyError('{} is not stored in FileProps'.format(key))
		# Returns a list of values. Return the first item in the list
		ret = cmds.getMetadata(
				streamName=self._cross3dStream, 
				memberName=self._memberName, 
				channelName=self._channelName, 
				index=key, 
				indexType=self._indexType, 
				scene=True)
		# they mostly return a list, mostly
		if isinstance(ret, list):
			# return the first value, this takes care of the ocational return value of None
			ret = ret[0]
		return self.unescapeValue(ret)
	
	def __iter__(self):
		return iter(self.keys())
	
	def __setitem__(self, key, value):
		if not self._hasStruct():
			cmds.dataStructure(
					format='raw', 
					asString='name={}:string=cross3dValue'.format(self._structureName))
		# Note: Make sure the metadata channel exists
		cmds.addMetadata(
				structure=self._structureName, 
				streamName=self._cross3dStream, 
				channelName=self._channelName, 
				indexType=self._indexType, 
				scene=True)
		# Store the metadata
		cmds.editMetadata(
				streamName=self._cross3dStream, 
				memberName=self._memberName, 
				index=key, 
				stringValue=self.escapeValue(value), 
				scene=True)
		# Notify listening slots about the change
		self.emitChange()
	
	def __init__(self, fileName=''):
		# These values are passed to various maya.cmds calls to retreive/set data
		self._structureName = 'Cross3dMetaData'
		self._cross3dStream = 'MetaCross3d'
		self._memberName = 'Cross3dValue'
		self._channelName = 'Cross3dChannel'
		self._indexType = 'string'
		super(MayaFileProps, self).__init__(None)
	
	def clear(self):
		for key in self:
			del self[key]
	
	def keys(self):
		if not self._hasStruct() or not self._hasMetaDataChannel():
			return []
		out = cmds.hasMetadata(scene=True, streamName=self._cross3dStream, asList=True)
		# Our stream name is always listed in hasMetadata, so remove it
		if self._cross3dStream in out:
			out.remove(self._cross3dStream)
		return out

# register the symbol
cross3d.registerSymbol('UserProps', MayaUserProps)
cross3d.registerSymbol('FileProps', MayaFileProps)
