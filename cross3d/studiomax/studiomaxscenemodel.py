##
#	\namespace	blur3d.api.studiomax.studiomaxsceneobject
#
#	\remarks	The StudiomaxSceneModel class provides the implementation of the AbstractSceneModel class as it applies
#				to 3d Studio Max scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		06/27/11
#

from blur3d.api import application, dispatch
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneModel( AbstractSceneModel ):

	def _addNativeObjects(self, nativeObjects):
		for nativeObject in nativeObjects:
			nativeObject.name = '.'.join([self.displayName(), nativeObject.name])

	def setDisplayName(self, displayName):

		# Renaming model objects.
		for obj in self.objects():
			nativePointer = obj.nativePointer()
			nativePointer.name = nativePointer.name.replace(self.displayName(), displayName)

		# Renaming model layers.
		for group in self.groups():
			nativePointer = group.nativePointer()
			nativePointer.setName(nativePointer.name.replace(self.displayName(), displayName))

		# Renaming model.
		self._nativePointer.name = displayName
		return True

	def setResolution(self, resolution):
		self.userProps()['resolution'] = resolution
		return True

	def resolution(self):
		return self.userProps().get('resolution', '')

	def export(self, fileName):
		name = self.displayName()
		objects = self._nativeObjects()
		groups = self._nativeGroups()

		# Removing the name space on objects.
		for obj in objects:
			obj.name = obj.name.replace(name + '.', '')

		# Removing the name space on layers.
		for group in groups:
			group.setName(group.name.replace(name, 'Model'))

		# Removing the name space on model.
		self._nativePointer.name = 'Model'

		# ExportNativeObjects call will trigger sceneSaveFinished and scene data is invalid until the name space is restored.
		dispatch.blockSignals(True)
		self._scene._exportNativeObjects(objects + [self._nativePointer], fileName)
		dispatch.blockSignals(False)

		# Restoring the name space on objects.
		for obj in objects:
			obj.name = '.'.join([name, obj.name])

		# Restoring the name space on layers.
		for group in groups:
			group.setName(group.name.replace('Model', name))

		# Restoring the name space on model.
		self._nativePointer.name = name

		# Running the delayed sceneSaveFinished signal.
		dispatch.dispatch('sceneSaveFinished', self._scene.currentFileName())

	def _nativeGroups(self, wildcard='*'):
		"""
			For groups in Max we return native layers instead since they do not exist.
		"""
		return self._scene._nativeLayers('.'.join([self.displayName(), wildcard]))

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', StudiomaxSceneModel )

