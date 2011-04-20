##
#	\namespace	blur3d.api.studiomax.softimagesceneviewport
#
#	\remarks	The SoftimageSceneViewport class provides the implementation of the AbstractSceneViewport class as it applies
#				to Softimage scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/11/10
#

from PySoftimage import xsi

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneViewport( object ): # not in abstract. has to be reviewed anyway
	def __init__( self, name ):
		self.name = name

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def name( self ):
		return self.name

	def cameraName( self ): # not in abstract. Anyway it's a pain, we will have to speak about it
		viewportManager = xsi.Desktop.ActiveLayout.Views( "vm" )
		focusedViewportLetter = viewportManager.GetAttributeValue( "focusedviewport" )
		return viewportManager.getAttributeValue( "activecamera:" + self.name )
		
	def setCamera( self, cameraName ): # not in abstract. Anyway it's a pain, we will have to speak about it.
		viewportManager = xsi.Desktop.ActiveLayout.Views( "vm" )
		focusedViewportLetter = viewportManager.GetAttributeValue( "focusedviewport" )
		viewportManager.SetAttributeValue( "activecamera:" + focusedViewportLetter, cameraName )
	
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
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', SoftimageSceneViewport )
