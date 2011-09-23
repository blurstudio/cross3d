##
#	\namespace	blur3d.api.softimage.softimagesceneviewport
#
#	\remarks	The SoftimageSceneViewport class provides the implementation of the AbstractSceneViewport class as it applies
#				to Softimage scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/11/10
#

from PySoftimage import xsi
from blur3d.api.abstract.abstractsceneviewport import AbstractSceneViewport

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneViewport( AbstractSceneViewport ):
	
	viewportNames = { 1:'A', 2:'B', 3:'C', 4:'D' }
	sceneCameras = [ 'Top', 'Left', 'Right', 'Bottom', 'User' ]
	
	def __init__( self, scene, viewportID=0 ): 
		self.viewportManager = xsi.Desktop.ActiveLayout.Views( 'vm' )
		if viewportID in self.viewportNames:
			self.name = self.viewportNames[ viewportID ]
		else:
			self.name = self.viewportManager.GetAttributeValue( 'focusedviewport' )

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
		
	def _nativeCamera( self ):
		cameraName = self.cameraName()
		if cameraName == 'Render Pass':
			from blur3d.api import Scene
			scene = Scene()
			renderPass = self.scene.currentRenderPass()
			cameraName = renderPass.camera().name()
		return xsi.Dictionary.GetObject( cameraName )

	def _setNativeCamera( self, nativeCamera ):
		if type( nativeCamera ) == str or type( nativeCamera ) == unicode:
			cameraName = nativeCamera
		else:
			cameraName = nativeCamera.FullName
		if nativeCamera:
			self.viewportManager.SetAttributeValue( 'activecamera:' + self.name, cameraName ) 
			return True
		else:
			return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def cameraName( self ):
		cameraName = self.viewportManager.getAttributeValue( 'activecamera:' + self.name )
		if cameraName in self.sceneCameras:
			cameraName = '.'.join( [ 'Views', 'View' + self.name, cameraName + 'Camera' ] )
		return cameraName

	def generatePlayblast( self, fileName, rang=None ):
		import os
		from blur3d.api import Scene
		scene = Scene()
		if not rang:
			rang = scene.animationRange()
		width = xsi.GetValue( "Passes.RenderOptions.ImageWidth" )
		height = xsi.GetValue( "Passes.RenderOptions.ImageHeight" )
		xsi.SetValue( "ViewportCapture.ImageWidth", width, None )
		xsi.SetValue( "ViewportCapture.ImageHeight", height, None )
		xsi.SetValue( "ViewportCapture.UseNativePlayer", False )
		xsi.SetValue( "ViewportCapture.LaunchFlipbook", False )
		xsi.SetValue( "ViewportCapture.CaptureAudio", None )
		xsi.SetValue( "ViewportCapture.UserPixelRatio", True )
		xsi.SetValue( "ViewportCapture.FormatType", 4 )
		xsi.SetValue( "ViewportCapture.Start", rang[0], None )
		xsi.SetValue( "ViewportCapture.End",rang[1] , None )
		xsi.SetValue( "ViewportCapture.Filename", fileName )
		letterToNumber = { "A":1, "B":2, "C":3, "D":4 }
		xsi.CaptureViewport( letterToNumber[ self.name ], False )
		return True
		
	def headlightIsActive( self, state ):
		camera = self._nativeCamera()
		xsi.SetValue( camera.FullName + '.camdisp.headlight', state )
		return True
		
	def setHeadlightIsActive( self ):
		camera = self._nativeCamera()
		return xsi.GetValue( camera.FullName + '.camdisp.headlight' )
		
	def slateIsActive( self ):
		import blur3d.api
		application = blur3d.api.application
		version = application.version()
		if version > 9:
			camera = self._nativeCamera()
			return xsi.GetValue( camera.FullName + '.camvis.camerainfo' )
		return False
	
	def setSlateIsActive( self, state ):
		import blur3d.api
		application = blur3d.api.application
		version = application.version()
		if version > 9:
			camera = self._nativeCamera()
			xsi.SetValue( camera.FullName + '.camvis.camerainfo', state )
			return True

	def setSlateText( self, text='' ):
		import blur3d.api
		application = blur3d.api.application
		version = application.version()
		if version > 9:
			camera = self._nativeCamera()
			xsi.SetValue( camera.FullName + '.camvis.camerainfotext', text )
			return True
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', SoftimageSceneViewport )
