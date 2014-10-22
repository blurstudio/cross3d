from collections import OrderedDict
import maya.cmds as cmds
from blur3d import api
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

resolutionAttr = 'Active_Resolution'

#------------------------------------------------------------------------

class MayaSceneModel(AbstractSceneModel):
	def _attrName(self):
		return '{node}.{attr}'.format(node=self._nativeName(), attr=resolutionAttr)
	
	def __init__(self, scene, nativeObject):
		super(MayaSceneModel, self).__init__(scene, nativeObject)
	
	def addResolution(self, name='', path='', load=False):
		if self.isReferenced():
			reses = self.userProps().get('Resolutions', OrderedDict())
			reses[name] = path
			self.userProps()['Resolutions'] = reses
			# Update the enum
			cmds.addAttr(self._attrName(), edit=True, enumName=':'.join(self.resolutions()))
			if load:
				self.setResolution(name)
			return True
		return False
	
	def isReferenced(self):
		# Check if it already has referenceing set up
		ret = resolutionAttr in cmds.listAttr(self._nativeName())
		if not ret:
			props = self.userProps()
			# Check if this object should support referencing
			ret = props.get('Referenced')
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
				del(props['Referenced'])
				# Create the user props for the reference
				props['Resolutions'] = OrderedDict(Offloaded='')
		return ret
	
	def offload(self):
		return False
	
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
			resolutions = self.userProps().get('Resolutions', {})
			if resolution in resolutions:
				return resolutions[resolution]
		return ''

	def resolutions(self):
		return self.userProps().get('Resolutions', {}).keys()
	
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
					filename = cmds.file(path, reference=True, namespace=":")
				# Find all top level items that were referenced into the scene and reparent them
				# under the model node
				objects = cmds.referenceQuery(filename, dagPath=True, nodes=True)
				topLevel = []
				for obj in objects:
					if cmds.nodeType(obj) in ('transform', 'dagContainer') and \
							not cmds.listRelatives(obj, parent=True, path=True):
								topLevel.append(obj)
				# Reparent the top level nodes under the model locator
				topLevel.append(self.name())
				if len(topLevel) > 1:
					cmds.parent(*topLevel)
				# Update the Active_Resolution property
				self.setProperty(resolutionAttr, i)
				# Store the loaded reference filename so we can remove it later
				self.userProps()['Loaded_Reference'] = filename
				# Copy the modelInfo user props to the model
				modelInfos = self.children(wildcard='{}|ModelInfo'.format(self.name()))
				if modelInfos:
					modelInfo = modelInfos[0]
					userProps = modelInfo.userProps()
					infos = userProps.get('infos')
					# TODO: Should we copy all properties? At this point things like project and 
					# department are already set even if this is the first time a resolution is loaded
					if infos:
						self.userProps()['infos'] = infos
				return True
		else:
			self.userProps()['resolution'] = resolution
		return False

	def setResolutionPath(self, path, name=''):
		return False

	def update(self):
		return False
	
	def _referenceNodeName(self):
		filename = self.userProps().get('Loaded_Reference')
		if filename:
			return cmds.referenceQuery(filename, referenceNode=True)
		return None

	
# register the symbol
api.registerSymbol('SceneModel', MayaSceneModel)