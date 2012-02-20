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
		self._scene = scene
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
		if cameraName:
			return xsi.Dictionary.GetObject( cameraName )
		else:
			return None

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

	def generatePlayblast( self, fileName, rang=None, **options ):
		import os
		from blur3d.api import Scene
		scene = Scene()
		if not rang:
			rang = scene.animationRange()
		
		width = xsi.GetValue( "Passes.RenderOptions.ImageWidth" )
		height = xsi.GetValue( "Passes.RenderOptions.ImageHeight" )
		fps = self._scene.animationFPS()
		
		viewportCapture = xsi.Dictionary.GetObject( 'ViewportCapture' ).NestedObjects
		
		viewportCapture( 'File Name' ).Value = fileName
		viewportCapture( 'Padding' ).Value = '(fn).#(ext)'
		viewportCapture( 'Width' ).Value = width
		viewportCapture( 'Height' ).Value = height
		viewportCapture( 'Scale Factor' ).Value = 1
		viewportCapture( 'User Pixel Ratio' ).Value = True 
		viewportCapture( 'Pixel Ratio' ).Value = 1 
		viewportCapture( 'Frame Rate' ).Value = fps 
		viewportCapture( 'Write Alpha' ).Value = False 
		viewportCapture( 'Record Audio Track' ).Value = False
		viewportCapture( 'Start Frame' ).Value = rang[0]
		viewportCapture( 'End Frame' ).Value = rang[1]
		viewportCapture( 'Launch Flipbook' ).Value = False
		viewportCapture( 'Use Native Movie Player' ).Value = False 
		viewportCapture( 'Movie' ).Value = False 
		viewportCapture( 'OpenGL Anti-Aliasing' ).Value = 1 
		viewportCapture( 'Remember Last Sequence' ).Value = False

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
