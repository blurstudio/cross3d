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
		return xsi.Dictionary.GetObject( self.cameraName() )
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def name( self ):
		return self.name

	def cameraName( self ):
		return self.viewportManager.getAttributeValue( 'activecamera:' + self.name )	
		
	def setCamera( self, cameraName ):
		self.viewportManager.SetAttributeValue( 'activecamera:' + self.name, cameraName )
		return True

	def playblast( self, fileName, range=None ):
		if not range:
			range = self.scene.animationRange()
		width = xsi.GetValue( "Passes.RenderOptions.ImageWidth" )
		height = xsi.GetValue( "Passes.RenderOptions.ImageHeight" )
		xsi.SetValue( "ViewportCapture.ImageWidth", width, None )
		xsi.SetValue( "ViewportCapture.ImageHeight", height, None )
		xsi.SetValue( "ViewportCapture.UseNativePlayer", False )
		xsi.SetValue( "ViewportCapture.LaunchFlipbook", False )
		xsi.SetValue( "ViewportCapture.CaptureAudio", None )
		xsi.SetValue( "ViewportCapture.UserPixelRatio", True )
		xsi.SetValue( "ViewportCapture.FormatType", 4 )
		xsi.SetValue( "ViewportCapture.Start", range[0], None )
		xsi.SetValue( "ViewportCapture.End",range[1] , None )
		xsi.SetValue( "ViewportCapture.Filename", fileName )
		letterToNumber = { "A":1, "B":2, "C":3, "D":4 }
		xsi.CaptureViewport( letterToNumber[ self.name ], False )
		return True
		
	def setHeadlight( self, switch ):
		camera = self.camera()
		xsi.SetValue( camera.name() + '.camdisp.headlight', switch )
		return True
		
	def hasHeadlight( self ):
		camera = self.camera()
		return xsi.GetValue( camera.name() + '.camdisp.headlight' )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', SoftimageSceneViewport )
