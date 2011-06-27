##
#	\namespace	blur3d.api.studiomax.abstractsceneviewport
#
#	\remarks	The AbstractSceneRenderPass class will define all the operations for viewport interaction.  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/11/10
#

from blur3d.api import SceneWrapper

#------------------------------------------------------------------------------------------------------------------------

class AbstractSceneViewport( SceneWrapper ):
	def __init__( self, scene, viewportID=0 ):
		pass

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _nativeCamera( self ):
		"""
			\remarks	return the viewport's native camera
			\return		<variant> camera | None
		"""
		return None
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def name( self ):
		"""
			\remarks	returns the name of the viewport. added by douglas
			\return		<str> name
		"""
		return ''

	def cameraName( self ):
		"""
			\remarks	returns the camera name of the viewport. added by douglas
			\return		<str> cameraName
		"""
		return ''
		
	def camera( self ):
		"""
			\remarks	return the viewport's camera
			\return		<blur3d.api.SceneCamera>
		"""
		from blur3d.api import SceneCamera
		print self._nativeCamera()
		return SceneCamera( self, self._nativeCamera() )	
		
	def setCamera( self, camera ):
		"""
			\remarks	sets the camera of the current viewport. added by douglas
			\return		<bool> success
		"""
		return False
		
	def playblast( self, fileName, range=None ):
		"""
			\remarks	generates a playblast in the specific path. added by douglas
			\return		<bool> success
		"""
		return False
		
	def setHeadlight( self, switch ):
		"""
			\remarks	sets the headlight of the camera of the viewport. added by douglas
			\param		switch <bool>
			\return		<bool> success
		"""
		return False
		
	def hasHeadlight( self ):
		"""
			\remarks	returns if the status of the headlight. added by douglas
			\return		<bool> status
		"""
		return False
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', AbstractSceneViewport )
