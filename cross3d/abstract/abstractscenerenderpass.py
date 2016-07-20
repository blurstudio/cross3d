##
#	\namespace	cross3d.softimage.abstractscenerenderpass
#
#	\remarks	The AbstractSceneRenderPass class will define all the operations for render passes interaction.  
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		04/08/11
#

import cross3d
from cross3d import SceneWrapper


class AbstractSceneRenderPass(SceneWrapper): # new douglas. technically it should be a scene object, but render passes have different methods than the one specified in AbstractSceneObject.
	"""
	The SceneRenderPass class will define all the operations for 
	render passes interaction. 
	"""

	def __init__(self, scene, nativeRenderPass):
		SceneWrapper.__init__(self, scene, nativeRenderPass)

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _nativeCamera(self): # new douglas
		return None

	def _setNativeCamera(self, nativeCamera): # new douglas
		return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def camera(self): # new douglas
		from cross3d import SceneCamera
		return SceneCamera(self._nativeCamera())

	def setCamera(self, sceneCamera): # new douglas
		return self._setNativeCamera(sceneCamera.nativePointer())

	def name(self): # new douglas
		return ""

	def displayName(self): # new douglas
		return ""

	def setDisplayName(self, name): # new douglas
		return False


# register the symbol
cross3d.registerSymbol('SceneRenderPass', AbstractSceneRenderPass)

