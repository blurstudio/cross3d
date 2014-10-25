import re
from collections import OrderedDict
import maya.cmds as cmds
import maya.OpenMaya as om
from blur3d import api
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

resolutionAttr = 'active_resolution'

#------------------------------------------------------------------------

class MayaSceneModel(AbstractSceneModel):
	""" Used to handle Maya's file Referencing
	
	Model Requirements in Maya:
		A model is a locator node named "Model" with a user prop named "Model" inside a namespace. 
		The namespace is used as the Model's name and displayName. If the model has a user prop named
		"referenced" with a value, the first time a reference method is called on the model "referenced"
		will be replaced with a "active_resolution" enum. and a "resolutions" user prop. I plan to
		change a model from a locator to a transform node after I resolve a few issues with user props
		and nodes like groundPlane_transform.
	
	Referencing:
		MayaSceneModel stores a OrderedDict containing Reference Name: filepath in the user prop
		"resolutions". It stores the current resolution in a enum attribute on the model called
		"active_resolution". Currently changing this attribute does nothing, but I plan to make it 
		call setResolution in the future. I am tracking the finding the current resolution by storing
		the resolution file path on the user prop "loaded_reference". This is neccissary to keep track
		of the {1} maya adds the second time a reference is loaded. This means that if you swap 
		reference in the Reference Editor, it will loose the reference. I plan to change this to lookup
		the reference node from the namespace.
		
	Parenting:
		Currently when a resolution is loaded, all Transform nodes and Asset Containers are reparented
		under the Model transform.
	
	MayaSceneModel.userProps:
		To make it possible for referenced models to be referenced in with user props, MayaSceneModel
		does some behind the scene's magic. When using resolutions, MayaSceneModel's user props will
		return userprops stored on the Model node, and a transform node under the model node called 
		"Metadata". When you add/set/delete a user prop, it will be stored/deleted on the Model, and 
		the Metadata object. If you request a prop that doesn't exist on the Model, but exists on the 
		Metadata object, it will return the value stored on the Metadata. If you then set a value on 
		that key it will be stored on both the Model and Metadata. In this way offloaded references 
		still retain most of the user props, and referenced user props automaticly get updated unless 
		they have been overridden.
		
		UserProps node example:
			C_Ly_Deadpool_:Model
			 \--- C_Ly_Deadpool_:Metadata
	"""
	def _attrName(self):
		return '{node}.{attr}'.format(node=self._nativeName(), attr=resolutionAttr)
	
	def __init__(self, scene, nativeObject):
		super(MayaSceneModel, self).__init__(scene, nativeObject)
	
	def addResolution(self, name='', path='', load=False):
		if self.isReferenced():
			reses = self.userProps().get('resolutions', OrderedDict())
			reses[name] = path
			self.userProps()['resolutions'] = reses
			# Update the enum
			cmds.addAttr(self._attrName(), edit=True, enumName=':'.join(self.resolutions()))
			if load:
				self.setResolution(name)
			return True
		return False
	
	def displayName(self):
		# Ignore the name of the object, we only care about the namespace for tools.
		return self._namespace(self._nativeTransform)['namespace']
	
	def setDisplayName(self, name):
		name = name.replace('-', '_')
		# If the model using a namespace, rename the namespace not the object.
		namespace = self._namespace(self._nativeTransform)['namespace']
		if namespace:
			if namespace == name:
				# Renaming the model to its current name, nothing to do.
				return
			# TODO: pull the reference node from the namespace instead of storing it in a user prop
			# that way if a user swaps reference in the Reference Editor we won't loose track of it
			filename = self.userProps().get('loaded_reference')
			if self.isReferenced() and filename:
				cmds.file(filename, edit=True, namespace=name, mergeNamespacesOnClash=True)
				# Doc's say cmds.file should move non-referenced nodes to the new namespace, but
				# in practice it doesn't. If the old namespace still exists, move all of its 
				# nodes into the new namespace and remove the old namespace
				if namespace in cmds.namespaceInfo(listOnlyNamespaces=True):
					cmds.namespace(moveNamespace=[namespace, name])
					cmds.namespace(removeNamespace=namespace)
			else:
				namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
				if name in namespaces:
					# If the namespace already exists we need to auto-increment the value or the
					# rename command will error out
					# reverse the name and pull off any trailing digits
					revName = re.match('(?P<revIter>\d*)(?P<name>.+)', name[::-1])
					if revName:
						n = revName.group('name')[::-1]
						v = int(revName.group('revIter')[::-1] or 1)
						while '{name}{revIter}'.format(name=n, revIter=v) in namespaces:
							v += 1
						name = '{name}{revIter}'.format(name=n, revIter=v)
					else:
						name = '{name}1'.format(name=name)
				cmds.namespace(rename=[namespace, name])
			return
		super(MayaSceneModel, self).setDisplayName(name)
	
	def isReferenced(self):
		# Check if it already has referenceing set up
		ret = resolutionAttr in cmds.listAttr(self._nativeName())
		if not ret:
			# NOTE: do not use self.userProps() to avoid recursion loop
			props = api.UserProps(self._nativePointer)
			# Check if this object should support referencing
			ret = props.get('referenced')
			if ret:
				# Object should support referencing, but referencing hasn't been setup, so create
				# the structure.
				cmds.addAttr(
						self._nativeName(), 
						longName=resolutionAttr, 
						attributeType="enum", 
						enumName="Offloaded")
				# Make the attribute viewable, but not keyable in the channelBox
				cmds.setAttr(self._attrName(), keyable=False, channelBox=True)
				# Remove the temp reference user prop
				del(props['referenced'])
				# Create the user props for the reference
				props['resolutions'] = OrderedDict(Offloaded='')
		return ret
	
	def name(self):
		return self.displayName()
	
	def offload(self):
		self.setResolution('Offloaded')
	
	def offloaded(self):
		return self.resolution() == 'Offloaded'
	
	def removeResolution(self, name):
		return False
	
	def resolution(self):
		if self.isReferenced():
			return cmds.getAttr(self._attrName(), asString=True)
		return ''

	def resolutionPath(self, resolution=''):
		if self.isReferenced():
			if not resolution:
				resolution = self.resolution()
			resolutions = self.userProps().get('resolutions', {})
			if resolution in resolutions:
				return resolutions[resolution]
		return ''

	def resolutions(self):
		return self.userProps().get('resolutions', {}).keys()
	
	def resolutionsPaths(self):
		return [self.resolutionPath(resolution) for resolution in self.resolutions() if resolution != 'Offloaded']

	def setResolution(self, resolution):
		if self.isReferenced():
			# handles qstrings
			resolution = unicode(resolution)
			# If I dont re-initialize a model object it does not return me the right resolutions.
			resolutions = self.resolutions()
			for i, res in enumerate(resolutions):
				# Handles cases sensitivity (crappy, but needed because resolution
				# names often come from filenames).
				if res.lower() != resolution.lower():
					continue
				path = self.resolutionPath(res)
				nodeName = self._referenceNodeName()
				if res.lower() == 'offloaded':
					# If offloaded, unload the reference
					if nodeName:
						cmds.file(unloadReference=nodeName)
					self.setProperty(resolutionAttr, i)
					return True
				# If the reference is already loaded, switch it with the requested one while
				# preserving any updated properties like animation.
				elif nodeName:
					cmds.file(path, loadReference=nodeName)
					filename = cmds.referenceQuery(nodeName, filename=True)
				else:
					# We use the filename to replace/unload the reference later. If c:\test.ma is
					# referenced twice the second uses the filename c:\test.ma{1}.
					filename = cmds.file(
							path, 
							reference=True, 
							mergeNamespacesOnClash=True, 
							usingNamespaces=True,
							namespace=self._namespace(self._nativeTransform)['namespace'])
				# Find all top level items that were referenced into the scene and reparent them
				# under the model node
				objects = cmds.referenceQuery(filename, dagPath=True, nodes=True)
				topLevel = []
				for obj in objects:
					if cmds.nodeType(obj) in ('transform', 'dagContainer') and \
							not cmds.listRelatives(obj, parent=True, path=True):
								topLevel.append(obj)
				# Reparent the top level nodes under the model locator
				topLevel.append(api.SceneWrapper._mObjName(self._nativeTransform))
				if len(topLevel) > 1:
					cmds.parent(*topLevel)
				# Update the active_resolution property
				self.setProperty(resolutionAttr, i)
				# Store the loaded reference filename so we can remove it later
				self.userProps()['loaded_reference'] = filename
#				# Copy the modelInfo user props to the model
#				modelInfos = self.children(wildcard='{name}:Model|{name}:UserProps'.format(name=self.name()))
#				if modelInfos:
#					modelInfo = modelInfos[0]
#					userProps = modelInfo.userProps()
#					infos = userProps.get('infos')
#					# TODO: Should we copy all properties? At this point things like project and 
#					# department are already set even if this is the first time a resolution is loaded
#					if infos:
#						self.userProps()['infos'] = infos
				return True
		else:
			self.userProps()['resolution'] = resolution
		return False

	def setResolutionPath(self, path, name=''):
		return False

	def setUserProps(self, newDict):
		"""
		Ovewrites the current custom properties with the provided dict
		:param newDict: dict
		"""
		props = MayaModelUserProps(self)
		props.clear()
		props.update(newDict)

	def userProps(self):
		"""Returns the UserProps object associated with this element
		:return; :class:`blur3d.api.UserProps`
		"""
		return MayaModelUserProps(self)

	def update(self):
		return False

	def _setModelUserProps(self, newDict):
		super(MayaSceneModel, self).setUserProps(newDict)

	def _referenceNodeName(self):
		filename = self.userProps().get('loaded_reference')
		if filename:
			return cmds.referenceQuery(filename, referenceNode=True)
		return None


class MayaModelUserProps(api.UserProps):
	""" This is a subclass of UserProps that takes a MayaSceneModel not a nativePointer.
	"""
	def __init__(self, blur3dModel):
		if not isinstance(blur3dModel, MayaSceneModel):
			raise Exception('Unlike UserProps, you must pass a MayaSceneModel to this class')
		self._model = blur3dModel
		# this stores the native pointer used to modify the SceneModel object
		self._metadataUserProps = None
		# The self._nativePointer will be set to the referenced Metadata object if it exists.
		nativePointer = self._model.nativePointer()
		if self._model.isReferenced():
			modelInfos = self._model.children(wildcard='|{name}:Model|{name}:Metadata'.format(name=self._model.name()))
			if modelInfos:
				self._metadataUserProps = api.UserProps(modelInfos[0].nativePointer())
		super(MayaModelUserProps, self).__init__(nativePointer)
	
	def __contains__(self, key):
		ret = super(MayaModelUserProps, self).__contains__(key)
		if not ret and self._metadataUserProps != None:
			ret = self._metadataUserProps.__contains__(key)
		return ret
	
	def __delitem__(self, key):
		metaHasAttribute = super(MayaModelUserProps, self).__contains__(key)
		modelHasAttribute = self._metadataUserProps.__contains__(key)
		if not metaHasAttribute and not modelHasAttribute:
			raise KeyError('{} is not stored in UserProps'.format(key))
		if metaHasAttribute:
			super(MayaModelUserProps, self).__delitem__(key)
		if modelHasAttribute:
			self._metadataUserProps.__delitem__(key)
		
	
	def __getitem__(self, key):
		if self._metadataUserProps != None:
			hasAtribute = super(MayaModelUserProps, self).__contains__(key)
			# If not stored on Metadata, check for and return it if its stored on the model
			if not hasAtribute and self._metadataUserProps.__contains__(key):
				return self._metadataUserProps.__getitem__(key)
		return super(MayaModelUserProps, self).__getitem__(key)
	
	def __setitem__(self, key, value):
		# Note: self.escapeKey(key) will be called when we create the attribute, so there is no
		# reason to call it twice.
		super(MayaModelUserProps, self).__setitem__(key, value)
		if self._metadataUserProps != None:
			# this will call self.emitChange() so no need to emit it twice.
			self._metadataUserProps.__setitem__(key, value)
		else:
			# Notify listening slots about the change
			self.emitChange()
	
	def keys(self):
		keys = super(MayaModelUserProps, self).keys()
		if self._metadataUserProps != None:
			modelKeys = self._metadataUserProps.keys()
			keys = list(set(keys).union(modelKeys))
		# TODO: Make MayaUserProps not show custom user props that are not strings
		if resolutionAttr in keys:
			keys.remove(resolutionAttr)
		return keys

# register the symbol
api.registerSymbol('SceneModel', MayaSceneModel)
