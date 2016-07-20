##
#	\namespace	cross3d.softimage.softimagescenerenderpass
#
#	\remarks	The SoftimageSceneRenderPass class will define all the operations for Softimage render passes interaction.  
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		04/08/11
#

from PySoftimage import xsi
from cross3d.abstract.abstractscenerenderpass import AbstractSceneRenderPass

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneRenderPass( AbstractSceneRenderPass ): 

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _nativeCamera( self ):
		cameraName = self.nativePointer().Camera.Value
		from cross3d import Scene
		scene = Scene()
		return scene.findObject( cameraName )
		
	def _setNativeCamera( self, nativeCamera ):
		self.nativePointer().Camera.Value = nativeCamera.FullName
		return True
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def name( self ):
		return self.nativePointer().FullName
		
	def displayName( self ):
		return self.nativePointer().Name

	def setDisplayName( self, name ):
		self.nativePointer().Name = name
		return True

# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneRenderPass', SoftimageSceneRenderPass )
