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

from blur3d.api import application
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneModel( AbstractSceneModel ):

	def setDisplayName(self, displayName):
		for obj in self.objects():
			nativePointer = obj.nativePointer()
			nativePointer.name = nativePointer.name.replace(self.displayName(), displayName)
		self._nativePointer.name = displayName
		return True

	def setResolution(self, resolution):
		self.userProps()['resolution'] = resolution
		return True

	def resolution(self):
		return self.userProps().get('resolution', '')

	def export(self, filename):
		name = self.displayName()
		objects = self._nativeObjects()

		# Removing the name space.
		for obj in objects:
			obj.name = obj.name.replace(name + '.', '')
		self._nativePointer.name = 'Model'

		self._scene._exportNativeObjects(objects + [self._nativePointer], filename)

		# Restoring the name space.
		for obj in objects:
			obj.name = '.'.join([name, obj.name])
		self._nativePointer.name = name

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', StudiomaxSceneModel )

