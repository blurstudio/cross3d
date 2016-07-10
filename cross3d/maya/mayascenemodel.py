import re
import maya.cmds as cmds
import maya.OpenMaya as om

import cross3d
from collections import OrderedDict
from cross3d.abstract.abstractscenemodel import AbstractSceneModel

resolutionAttr = 'resolution'

#------------------------------------------------------------------------

class MayaSceneModel(AbstractSceneModel):
	""" Used to handle Maya's file Referencing

	Model Requirements:
		A model is a namespaced transform node named "Model" with a user prop named "model". 
		The namespace is used as the model's name and displayName. If the model has a user prop named
		"referenced" with a value, the first time a reference method is called on the model an
		"resolution" enum. and a "resolutions" user prop will be created.
	
	Referencing:
		MayaSceneModel stores a "resolutions" OrderedDict userProp containing resolution name keys 
		and filePath values. It stores the current resolution in a enum attribute on the model called
		"resolution". Currently changing this attribute does nothing, but I plan to make it 
		call setResolution in the future. I am tracking the reference path of the current resolution
		by cross-referencing both "resolution" and "resolutions". This is neccissary to keep track
		of the {1} maya adds the second time a reference is loaded. This means that if you swap 
		reference in the Reference Editor, it will loose the reference. I plan to change this to lookup
		the reference node from the namespace.
	"""

	def _modifiedAttrs(self):
		""" Returns a dictionary of modifications made to this referenced model.
		
		For referneced models return info describing the modifications made by the referencing
		system.
		"""
		modified = {}
		if self.isReferenced():
			fullName = self.path()
			refNode = cmds.referenceQuery(fullName, referenceNode=True)
			# Build the setAttr pattern
			pattern = r'setAttr {node}.(?P<attr>[^ ]+)'.format(node = fullName.replace('|', r'\|'))
			setAttrRegex = re.compile(pattern)
			# TODO: Add patterns for other mel commands like addAttr, etc
			for s in cmds.referenceQuery(refNode, editStrings=True):
				# Process setAttr
				match = setAttrRegex.match(s)
				if match:
					key = match.groupdict()['attr']
					if s.endswith('"'):
						# Found a string. Note, this does not include escaped quotes.
						openingQuote = s[::-1].find('"', 1)
						value = s[-openingQuote:-1]
					else:
						# its not a string
						value = s.split(' ')[-1]
					modified.setdefault(key, {}).setdefault('setAttr', {}).update(value=value, command=s)
		return modified

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
		return self._namespace(self._nativeTransform).get('namespace', '')
	
	def setDisplayName(self, name):
		name = name.replace('-', '_')
		# If the model using a namespace, rename the namespace not the object.
		namespace = self._namespace(self._nativeTransform)['namespace']
		if namespace:
			if namespace == name:
				# Renaming the model to its current name, nothing to do.
				return

			# TODO: pull the reference node from the namespace instead of storing it in a user prop
			# that way if a user swaps reference in the Reference Editor we won't loose track of it.
			filename = self.resolutionPath(self.resolution())

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
	
	def _createResolutionComboBox(self):
		userProps = cross3d.UserProps(self._nativePointer)

		# Local models have a resolution metadata.
		# Maybe it's not a good idea.
		if resolutionAttr in userProps:
			del userProps[resolutionAttr]

		resolutions = ':'.join(userProps.get('resolutions', []))

		# Object should support referencing, but referencing hasn't been setup, so create the structure.
		cmds.addAttr(self._nativeName(), longName=resolutionAttr, attributeType="enum", enumName=resolutions)

		# Make the attribute viewable, but not keyable in the channelBox
		try:
			cmds.setAttr(self._attrName(), keyable=False, channelBox=True)
		# Consume a runtime error if the resolution attribute was in the reference. This is only a
		# issue with some of our first models, Asset Exporter will remove them from future exports.
		except RuntimeError as error:
			pattern = r"setAttr: The attribute '[^']+' is from a referenced file, thus the keyable state cannot be changed."
			if not re.match(pattern, error.message):
				raise

	def isReferenced(self):
		userProps = cross3d.UserProps(self._nativePointer)
		if userProps.get('referenced', False):

			# Checking if we need to set the resolution combobox.
			if not resolutionAttr in cmds.listAttr(self._nativeName()):

				# Create the user props for the reference.
				userProps['resolutions'] = OrderedDict(Offloaded='')
				self._createResolutionComboBox()

			return True
		return False

	def export(self, fileName):
		name = self.name()
		objects = self.objects()
		selection = self._scene.selection()

		# Selecting the object.
		self._scene.setSelection(objects)

		# Make sure we set the current namespace to root otherwise the next line does not work.
		initialNamespace = cmds.namespaceInfo(currentNamespace=True)
		cmds.namespace(setNamespace=":" )

		# Trashing the namespace.
		cmds.namespace(removeNamespace=name, mergeNamespaceWithRoot=True)
		
		# Remove attributes that should not be stored in a exported model.
		userProps = self.userProps()
		resolutions = None
		resolution = {}
		if 'resolutions' in userProps:
			resolutions = userProps.pop('resolutions')
		if resolutionAttr in userProps:
			# Resolution is a bit complicated because it can be a enum.
			if cmds.attributeQuery(resolutionAttr, node= self._nativeName(), attributeType=True) == 'enum':
				# Store the enum list
				resolution['names'] = cmds.attributeQuery( resolutionAttr, node=self._nativeName(), listEnum=True)
			resolution['value'] = self.userProps().pop(resolutionAttr)
		# Export the model
		cmds.file(fileName, force=True, exportSelected=True, typ="mayaAscii", usingNamespaces=False)
		
		# Restore the attributes we used earlier
		userProps = self.userProps()
		if resolutions != None:
			userProps['resolutions'] = resolutions
		if resolution:
			if 'names' in resolution:
				cmds.addAttr(self._nativeName(), longName=resolutionAttr, attributeType="enum", enumName=resolution['names'][0])
				cmds.setAttr(self._attrName(), keyable=False, channelBox=True)
				cmds.setAttr(self._attrName(), resolution['value'])
			else:
				userProps[resolutionAttr] = resolution['value']
		
		# Re-add all items to the namespace
		for obj in objects:
			# TODO: Optomize setNamespace, it checks for if the namespace exists before renameing.
			# In this case this is unneccissary.
			obj.setNamespace(name)

		# Restoring the namespace.
		cmds.namespace(setNamespace=initialNamespace)

		# Restoring selection
		self._scene.setSelection(selection)
		return True

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
			props = self.userProps()
			resolutions = props.get('resolutions', {})
			if resolution in resolutions:
				ret = resolutions[resolution]
				reference = props.get('reference', '')
				if reference.replace('\\', '/').startswith(ret.replace('\\', '/')):
					return reference
				return ret
		return ''

	def resolutions(self):
		return self.userProps().get('resolutions', {}).keys()
	
	def resolutionsPaths(self):
		return [self.resolutionPath(resolution) for resolution in self.resolutions() if resolution != 'Offloaded']

	def setResolution(self, resolution):

		if self.isReferenced():

			# Handling QStrings.
			resolution = unicode(resolution)
			currentResolution = self.resolution()
			resolutions = self.resolutions()
			referenceNodeName = self._referenceNodeName()

			# Looping through the model resolutions.
			for i, res in enumerate(resolutions):

				# Skipping if the resolution name does not match.
				# Handles cases sensitivity, crappy but because of filenames.
				if res.lower() != resolution.lower():
					continue

				# Getting the resolution path.
				path = self.resolutionPath(res)

				# If we are going for offloaed.
				if res == 'Offloaded':
				
					# Copy the user props before offloading the reference so we can add them to the
					# temp node later.
					userProps = self.userProps().lookupProps()
					if resolutionAttr in userProps:
						# Important: We want to drop the resolution key as it's only used for local models.
						userProps.pop(resolutionAttr)

					# Storing the name of the model root.
					name = self._mObjName(self._nativePointer, False)

					# Un-loading the reference.
					if referenceNodeName:
						cmds.file(unloadReference=referenceNodeName)

					# Recreating the local model root.
					self._nativePointer = cross3d.SceneWrapper._asMOBject(cmds.createNode('transform', name=name))
					self._nativeTransform = self._nativePointer

					# Re-applying user props.
					cross3d.UserProps(self._nativePointer).update(userProps)

					# Re-creating resolution channel box.
					self._createResolutionComboBox()

					# Setting the current resolution property.
					self.setProperty(resolutionAttr, i)
					return True

				# If we are coming from offloaded.
				elif currentResolution == 'Offloaded':

					# We store the user props.
					oldProps = self.userProps().lookupProps()

					# We delete the offloaded local model root.
					name = self._mObjName(self._nativePointer, False)
					namespace = self._namespace(self._nativeTransform)['namespace']
					self._scene._removeNativeObjects([self._nativePointer])

					# If the a reference node does not exists. We create a reference.
					if not referenceNodeName:
						reference = cmds.file(
								path, 
								reference=True, 
								mergeNamespacesOnClash=True, 
								usingNamespaces=True, 
								namespace=namespace)

					# Else simply switching the reference preserving any local change.
					else:
						cmds.file(path, loadReference=referenceNodeName)
						reference = cmds.referenceQuery(referenceNodeName, filename=True)

					# Making sure native pointers are re-assigned.
					self._nativePointer = self._scene._findNativeObject(name)
					self._nativeTransform = self._nativePointer

					# Re-applying user props.
					userProps = cross3d.UserProps(self._nativePointer)
					mods = self._modifiedAttrs()
					# I've left the debug message inside here in case we need to debug this later
					cross3d.logger.debug('{res} {line}'.format(res=resolution, line='-'*80))
					cross3d.logger.debug(unicode(mods.keys()))
					for key, value in oldProps.iteritems():
						cross3d.logger.debug('	0 "{}"'.format(key))
						if key in userProps:
							cross3d.logger.debug('	1')
							if key == resolutionAttr:
								# The keys are the same
								cross3d.logger.debug('	2 Skipping, Its the resolution attr')
								continue
							if userProps[key] == value:
								# Do not override values that are the same
								cross3d.logger.debug('	3 Skipping {} is the same value'.format(key))
								continue
							if key in mods:
								cross3d.logger.debug('\t4 {comp}\n\t\t\t{upVal}\n\t\t\t{modVal}'.format(
										comp = userProps.escapeValue(value) == mods[key]['setAttr']['value'],
										upVal = [userProps.escapeValue(value)],
										modVal = [mods[key]['setAttr']['value']]
										))
								if userProps.escapeValue(value) == mods[key]['setAttr']['value']:
									# Ignore any modified values that haven't changed while the 
									# reference was offloaded
									cross3d.logger.debug('	skipping, not changed while offloaded {}'.format(key))
									continue
							elif key in userProps:
								cross3d.logger.debug('	5 Skipping, Value didnt change while offloaded Key: {key} Values: {value}'.format(
										key=key, value=unicode([userProps[key], value])))
								continue
						# printing debug data block #-----------------------------------------------
						if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
							old = ''
							if key in userProps:
								old = userProps[key]
							cross3d.logger.debug('# Setting {key} value from {old} to {value}'.format(key=key, old=old, value=value))
						# End printing debug data block---------------------------------------------
						userProps[key] = value
					
					cross3d.UserProps(self._nativePointer).update(userProps)

					# Re-creating resolution channel box.
					self._createResolutionComboBox()

					# This will be important later when we come out offload and try to access the reference node.
					# Also you will notice we set the reference path using the reference variable and not the path one.
					# Well believe or not the second time you load a reference the actual "resolved" path get a {1} suffix.
					# You can see that if you look in File > Reference Editor.
					cross3d.UserProps(self._nativePointer)['reference'] = reference

					# Setting the current resolution property.
					self.setProperty(resolutionAttr, i)
					return True

				# If we are just switching resolution.
				else:
					# Get the name of the model node so we can update the native pointer after
					# loading the new reference
					name = self._mObjName(self._nativePointer, False)
					# Simply switching the reference preserving any local change.
					cmds.file(path, loadReference=referenceNodeName)
					
					# Find the newly referenced model node
					# Making sure native pointers are re-assigned.
					self._nativePointer = self._scene._findNativeObject(name)
					self._nativeTransform = self._nativePointer

					# This will be important later when we come out offload and try to access the reference node.
					# Also you will notice we set the reference path using the reference variable and not the path one.
					# Well believe or not the second time you load a reference the actual "resolved" path get a {1} suffix.
					# You can see that if you look in File > Reference Editor.
					cross3d.UserProps(self._nativePointer)['reference'] = cmds.referenceQuery(referenceNodeName, filename=True)

					# Setting the current resolution property.
					self.setProperty(resolutionAttr, i)
					return True

		else:	
			self.userProps()[resolutionAttr] = resolution
		return True

	def setResolutionPath(self, path, name=''):
		return False

	def update(self):
		return False

	def _setModelUserProps(self, newDict):
		super(MayaSceneModel, self).setUserProps(newDict)

	def _referenceNodeName(self):
		filename = self.userProps().get('reference')
		if filename:
			return cmds.referenceQuery(filename, referenceNode=True)
		return None

# register the symbol
cross3d.registerSymbol('SceneModel', MayaSceneModel)
