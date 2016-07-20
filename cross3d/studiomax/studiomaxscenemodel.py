##
#	\namespace	cross3d.studiomax.studiomaxsceneobject
#
#	\remarks	The StudiomaxSceneModel class provides the implementation of the AbstractSceneModel class as it applies
#				to 3d Studio Max scenes
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		06/27/11
#

from cross3d import application, dispatch
from cross3d.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneModel( AbstractSceneModel ):

	def __init__(self, scene, nativeObject):
		super(self.__class__, self).__init__(scene, nativeObject)

		# The vault is used when exploding or recomposing a model.
		self._vault = {}

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

	def explode(self):
		self._vault['name'] = self.displayName()
		self._vault['nativeObjects'] = self._nativeObjects()
		self._vault['nativeGroups'] = self._nativeGroups()

		# Removing the name space on objects.
		for obj in self._vault['nativeObjects']:
			obj.name = obj.name.replace(self._vault['name'] + '.', '')

		# Removing the name space on layers.
		for group in self._vault['nativeGroups']:
			group.setName(group.name.replace(self._vault['name'], 'Model'))

		# Removing the name space on model.
		self._nativePointer.name = 'Model'

	def recompose(self):
		name =  self._vault.get('name')
		if name:

			# Restoring the name space on objects.
			for obj in self._vault.get('nativeObjects'):
				obj.name = '.'.join([name, obj.name])

			# Restoring the name space on layers.
			for group in self._vault.get('nativeGroups'):
				group.setName(group.name.replace('Model', name))

			# Restoring the name space on model.
			self._nativePointer.name = name

			# Running the delayed sceneSaveFinished signal.
			dispatch.dispatch('sceneSaveFinished', self._scene.currentFileName())

			# Clearing the temporary holders.
			self._vault['name'] = None
			self._vault['nativeObjects'] = None
			self._vault['nativeGroups'] = None

	def export(self, fileName):

		# Exploding in Max means basically loosing the name space.
		self.explode()

		# ExportNativeObjects call will trigger sceneSaveFinished and scene data is invalid until the name space is restored.
		dispatch.blockSignals(True)
		self._scene._exportNativeObjects(self._vault.get('nativeObjects') + [self._nativePointer], fileName)
		dispatch.blockSignals(False)

		# Recomposing reverts the name space.
		self.recompose()

	def _nativeGroups(self, wildcard='*'):
		"""
			For groups in Max we return native layers instead since they do not exist.
		"""
		return self._scene._nativeLayers('.'.join([self.displayName(), wildcard]))

# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneModel', StudiomaxSceneModel )
