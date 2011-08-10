##
#	\namespace	blur3d.api.studiomax.abstractsceneviewport
#
#	\remarks	The AbstractSceneRenderPass class will define all the operations for viewport interaction  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/11/10
#

from PyQt4.QtCore import QObject

#------------------------------------------------------------------------------------------------------------------------

class AbstractSceneViewport( QObject ):
	def __init__( self, scene, viewportID=0 ):
		super( AbstractSceneViewport, self ).__init__()
		
		self._scene = scene
		self.name = ''
		self._slateIsActive = False
		self._slateText = ''
		
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

	def cameraName( self ):
		"""
			\remarks	return the viewport's camera name. added by douglas
			\return		<variant> camera | None
		"""
		return ''

	def generatePlayblast( self, fileName, ran=None ):
		"""
			\remarks	generates a playblast in the specific path. added by douglas
			\param		filename where the playblast is save
			\param		ran is the range of the playblast
			\return		<bool> success
		"""
		return False
	
	def setHeadlightIsActive( self, active ):
		"""
			\remarks	sets the headlight of the camera of the viewport. added by douglas
			\param		active <bool>
			\return		<bool> success
		"""
		return False
		
	def headlightIsActive( self ):
		"""
			\remarks	returns if the status of the headlight. added by douglas
			\return		<bool> active
		"""
		return False
		
	def size( self ):
		"""
			\remarks	returns the viewport size. added by douglas
			\return		( <int>, <int> ) size
		"""
		return ( 0, 0 )
		
	def safeFrameSize( self ):
		"""
			\remarks	returns the size of the safe frame. added by douglas
			\return		( <int>, <int> ) size
		"""
		return ( 0, 0 )
		
	def safeFrameIsActive( self ):
		"""
			\remarks	returns the active of the safe frame. added by douglas
			\return		<bool> active
		"""
		return False
		
	def setSafeFrameIsActive( self, active ):
		"""
			\remarks	sets the active of the safe frame. added by douglas
			\param		<bool> active
			\return		<bool> success
		"""
		return False
		
	def slateIsActive( self ):
		return False
	
	def setSlateIsActive( self, active ):
		return False
		
	def setSlateText( self, text='' ):
		return False
		
	def slateDraw( self ):
		return False

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', AbstractSceneViewport )
