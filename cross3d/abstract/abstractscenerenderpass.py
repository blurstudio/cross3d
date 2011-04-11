##
#	\namespace	blur3d.api.softimage.abstractscenerenderpass
#
#	\remarks	The AbstractSceneRenderPass class will define all the operations for Softimage render passes interaction.  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/08/11
#

from blur3d.api import SceneWrapper

#------------------------------------------------------------------------------------------------------------------------

class AbstractSceneRenderPass( SceneWrapper ): # new douglas. technically it should be a scene object, but render passes have different methods than the one specified in AbstractSceneObject.
	def __init__( self, scene, nativeRenderPass ):
		SceneWrapper.__init__( self, scene, nativeRenderPass )

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _nativeCamera( self ): # new douglas
		return None
		
	def _setNativeCamera( self, nativeCamera ): # new douglas
		return False
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def camera( self ): # new douglas
		from blur3d.api import SceneCamera
		return SceneCamera( self._nativeCamera() )
	
	def setCamera( self, sceneCamera ): # new douglas
		return self._setNativeCamera( sceneCamera.nativePointer() )

	def name( self ): # new douglas
		return ""

	def displayName( self ): # new douglas
		return ""

	def setDisplayName( self, name ): # new douglas
		return False
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneRenderPass', AbstractSceneRenderPass )
		
