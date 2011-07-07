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
		self.name = ''

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _nativeCamera( self ):
		"""
			\remarks	return the viewport's native camera. added by douglas
			\return		<variant> camera | None
		"""
		return None

	def _setNativeCamera( self, nativeCamera ):
		"""
			\remarks	sets the native camera of the current viewport. added by douglas
			\param		nativeCamera <variant> | <str>
			\return		<bool> success
		"""
		return False
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def camera( self ):
		"""
			\remarks	return the viewport's camera
			\return		<blur3d.api.SceneCamera>
		"""
		from blur3d.api import SceneCamera
		camera = self._nativeCamera()
		if camera:
			return SceneCamera( self, camera )
		return None

	def cameraName( self ):
		"""
			\remarks	return the viewport's camera name. added by douglas
			\return		<variant> camera | None
		"""
		return ''

	def setCamera( self, camera ):
		"""
			\remarks	sets the camera of the current viewport. added by douglas
			\param		camera <blur3d.api.SceneCamera> | <str>
			\return		<bool> success
		"""	
		if type( camera ) == str or type( camera ) == unicode:
			cam = camera
		else:
			cam = camera.nativePointer()
		return self._setNativeCamera( cam )

	def playblast( self, fileName, ran=None ):
		"""
			\remarks	generates a playblast in the specific path. added by douglas
			\param		filename where the playblast is save
			\param		ran is the range of the playblast
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
