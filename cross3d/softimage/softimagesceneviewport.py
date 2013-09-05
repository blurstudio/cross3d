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

import os
import time

from PySoftimage import xsi
from blur3d.api import Exceptions
from blur3d.api.abstract.abstractsceneviewport import AbstractSceneViewport

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneViewport( AbstractSceneViewport ):
	
	viewportNames = { 1:'A', 2:'B', 3:'C', 4:'D' }
	sceneCameras = [ 'Top', 'Left', 'Right', 'Bottom', 'User' ]
	
	def __init__( self, scene, viewportID=0 ): 
		self._state = {}
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
		return self.viewportManager.getAttributeValue( 'activecamera:' + self.name )

	def generatePlayblast( self, fileName, frameRange=None, resolution=None, slate=None, effects=True, geometryOnly=True ):
		"""
			Creates an unpadded JPG file sequence from the viewport for a given range.
		"""
		
		# Collecting data.
		nativeCamera = self._nativeCamera()
		firstFrameFileName = fileName.replace('.jpg', '.%d.jpg' % frameRange[0])
		lastFrameFileName = fileName.replace('.jpg', '.%d.jpg' % frameRange[1])
		
		try:
			firstFrameStartTime = os.path.getmtime(firstFrameFileName)
			lastFrameStartTime = os.path.getmtime(lastFrameFileName)
		except os.error:
			firstFrameStartTime = 0
			lastFrameStartTime = 0
		
		# Storing object states.
		self._scene.storeState()
		self.storeState()
		
		# Setting the scene range. Apparently if you don't it causes an animation layer issue.
		self._scene.setAnimationRange(frameRange)
		
		# Setting slate.
		if slate:
			self.setSlateText( slate )
			self.setSlateIsActive( True )
			xsi.SetValue( nativeCamera.FullName + '.camvis.currenttime', False )
		elif slate == None:
			xsi.SetValue( nativeCamera.FullName + '.camvis.currenttime', False )
		else:
			xsi.SetValue( nativeCamera.FullName + '.camvis.currenttime', True )
		
		# Setting regular visibility options.
		nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'gridvis' ).Value = False
		nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'gridaxisvis' ).Value = False
		nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'constructionlevel' ).Value = False
		nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objannotationobjects' ).Value = False
		xsi.SetValue( 'preferences.ViewCube.show', False )
		
		if geometryOnly:
			
			# Setting geometry only visibility options.
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objpolymesh' ).Value = True
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objparticles' ).Value = True
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objinstances' ).Value = True
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objlights' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objcameras' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objimpgeometry' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objcurves' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objhair' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objnulls' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrltransfogroups' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrlchnjnts' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrlchnroots' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrlchneff' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrllattices' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrltextsupp' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrlchnjnts' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrlwaves' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objctrlother' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'objenvironment' ).Value = False
			nativeCamera.Properties( 'Camera Visibility' ).Parameters( 'custominfo' ).Value = False
		
		# Checking inputs.
		if not frameRange:
			frameRange = self._scene.animationRange()
		if not resolution:
			from PyQt4.QtCore import QSize
			resolution = QSize( xsi.GetValue( "Passes.RenderOptions.ImageWidth" ), xsi.GetValue( "Passes.RenderOptions.ImageHeight" ) )

		# Set camera's picture ratio.
		camera = self.camera()
		if camera:
			pictureRatio = float( resolution.width() ) / resolution.height() 
			camera.setPictureRatio( pictureRatio )
		
		fps = self._scene.animationFPS()
		
		viewportCapture = xsi.Dictionary.GetObject( 'ViewportCapture' ).NestedObjects
		
		viewportCapture( 'File Name' ).Value = fileName
		viewportCapture( 'Padding' ).Value = '(fn).#(ext)'
		viewportCapture( 'Width' ).Value = resolution.width()
		viewportCapture( 'Height' ).Value = resolution.height()
		viewportCapture( 'Scale Factor' ).Value = 1
		viewportCapture( 'User Pixel Ratio' ).Value = True 
		viewportCapture( 'Pixel Ratio' ).Value = 1 
		viewportCapture( 'Frame Rate' ).Value = fps 
		viewportCapture( 'Write Alpha' ).Value = False 
		viewportCapture( 'Record Audio Track' ).Value = False
		viewportCapture( 'Start Frame' ).Value = frameRange[0]
		viewportCapture( 'End Frame' ).Value = frameRange[1]
		viewportCapture( 'Launch Flipbook' ).Value = False
		viewportCapture( 'Use Native Movie Player' ).Value = False 
		viewportCapture( 'Movie' ).Value = False 
		viewportCapture( 'OpenGL Anti-Aliasing' ).Value = 1 
		viewportCapture( 'Remember Last Sequence' ).Value = False

		letterToNumber = { "A":1, "B":2, "C":3, "D":4 }
		xsi.CaptureViewport( letterToNumber[ self.name ], False )
		
		# Restoring states.
		self._scene.restoreState()
		self.restoreState()
		
		# If the famouse capture Softimage bug happened we raise a specific error.
		try:
			firstFrameEndTime = os.path.getmtime(firstFrameFileName)
			if not firstFrameStartTime < firstFrameEndTime:
				raise Exceptions.OutputFailed('The playblast failed due to a native Softimage bug. Do not panic, the fix is easy. Open the regular capture window, change the format to anything. Close the window and try again.')
		except os.error:
			raise Exceptions.OutputFailed('The playblast failed due to a native Softimage bug. Do not panic, the fix is easy. Open the regular capture window, change the format to anything. Close the window and try again.')
			
		# If the capture was not completed we just return False.
		try:
			lastFrameEndTime = os.path.getmtime(lastFrameFileName)
			if not lastFrameStartTime < lastFrameEndTime:
					return False
		except os.error:
			return False
			
		return True

	def storeState( self ):
		for parameter in self._nativeCamera().Properties( 'Camera Visibility' ).Parameters:
			self._state[ parameter.ScriptName ] = parameter.Value
		self._state[ 'viewcubeshow' ] = xsi.GetValue( 'preferences.ViewCube.show' )
		return True
		
	def restoreState( self ):
		for key in self._state:
			if not key in [ 'viewcubeshow' ]:
				self._nativeCamera().Properties( 'Camera Visibility' ).Parameters( key ).Value = self._state[ key ]
		xsi.SetValue( 'preferences.ViewCube.show', self._state[ 'viewcubeshow' ] )
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
