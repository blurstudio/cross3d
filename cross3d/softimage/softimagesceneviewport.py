##
#	\namespace	cross3d.softimage.softimagesceneviewport
#
#	\remarks	The SoftimageSceneViewport class provides the implementation of the AbstractSceneViewport class as it applies
#				to Softimage scenes
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		04/11/10
#

import os
import re
import time

from PySoftimage import xsi
from Qt.QtCore import QSize
from cross3d import Exceptions
from cross3d.classes import FrameRange
from cross3d.abstract.abstractsceneviewport import AbstractSceneViewport

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneViewport( AbstractSceneViewport ):
	
	viewportNames = { 1:'A', 2:'B', 3:'C', 4:'D' }
	sceneCameras = [ 'Top', 'Left', 'Right', 'Bottom', 'User', 'Front' ]
	
	def __init__( self, scene, viewportID=0 ): 
		super(SoftimageSceneViewport, self).__init__(scene, viewportID)
		self._scene = scene
		
		for view in xsi.Desktop.ActiveLayout.Views:
			if view.type == "View Manager":
				self.viewportManager = view
		
		assert self.viewportManager, 'There is no viewport in your current Softimage layout.'

		if viewportID in self.viewportNames:
			self.name = self.viewportNames[ viewportID ]
		else:
			self.name = self.viewportManager.GetAttributeValue( 'focusedviewport' )

		self._nativePointer = self.viewportManager()

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
		
	def _nativeCamera( self ):
		cameraName = self.cameraName()
		if cameraName in self.sceneCameras:
			cameraName = "Views.View%s.%sCamera" % (self.name, cameraName)

		if cameraName == 'Render Pass':
			from cross3d import Scene
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

	def createCamera(self, name='Camera', type='Standard'):
		camera = self._scene.createCamera(name, type)
		camera.matchCamera(self.camera())
		camera.setDisplayName(name)
		return camera

	def generateSnapshot(self, fileName, resolution=None, slate=None, effects=True, geometryOnly=True, pathFormat=r'{basePath}\{fileName}.{frame}.{ext}'):
		
		"""
			Creates an unpadded JPG file sequence from the viewport for a given range.
			TODO: If resolution is not provided use viewport resolution.
			TODO: Don't have frame number show in the final file name path.
		"""

		frame = self._scene.currentFrame()
		return self.generatePlayblast(fileName, frameRange=[frame, frame], resolution=resolution, slate=slate, effects=effects, geometryOnly=geometryOnly, pathFormat=pathFormat)

	def generatePlayblast( self, fileName, frameRange=None, resolution=None, slate=None, effects=True, geometryOnly=True, pathFormat=r'{basePath}\{fileName}.{frame}.{ext}'):
		
		"""
			Creates an unpadded JPG file sequence from the viewport for a given range.
		"""
		
		# Treating inputs.
		if isinstance(frameRange, int):
			frameRange = FrameRange([frameRange, frameRange])

		# Checking frame range.
		initialFrameRange = self._scene.animationRange()
		if not frameRange:
			frameRange = initialFrameRange

		# Collecting data.
		nativeCamera = self._nativeCamera()
		def genImagePath(frame=None):
			basePath, fn = os.path.split(fileName)
			pf = pathFormat
			# Deal with xsi's special number padding format
			if frame == None:
				filen = '(fn)'
				ext = '(ext)'
				# Remove any number specific formatting so we can insert a simple # for each padding digit
				pf = re.sub(r'{frame:[^}]*', r'{frame', pf)
				padding = re.findall(r'{frame:(\d+)', pathFormat)
				if padding:
					frameNo = '#' * int(padding[0])
				else:
					frameNo = '#'
			else:
				fileSplit = fn.split('.')
				filen = '.'.join(fileSplit[:-1])
				ext = fileSplit[-1]
				frameNo = frame
			out = pf.format(basePath=basePath, fileName=filen, frame=frameNo, ext=ext)
			index = pathFormat.find('{ext}')
			if frame == None and index > 0 and pathFormat[index-1] == '.':
				# strip out the file extension dot
				fileSplit = out.split('.')
				out = '.'.join(fileSplit[:-1]) + fileSplit[-1]
			return out
		firstFrameFileName = genImagePath(frameRange[0])
		lastFrameFileName = genImagePath(frameRange[1])
		
		try:
			firstFrameStartTime = os.path.getmtime(firstFrameFileName)
			lastFrameStartTime = os.path.getmtime(lastFrameFileName)
		except os.error:
			firstFrameStartTime = 0
			lastFrameStartTime = 0
		
		# Storing object states.
		self._scene.storeState()
		self.storeViewOptions()
			
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
		
		# Checking resolution.
		if not resolution:
			resolution = QSize( xsi.GetValue( "Passes.RenderOptions.ImageWidth" ), xsi.GetValue( "Passes.RenderOptions.ImageHeight" ) )

		# Setting the scene range. Apparently if you don't it causes an animation layer issue.
		if not initialFrameRange.contains(frameRange):
			self._scene.setAnimationRange(frameRange)
		
		# Set camera's picture ratio.
		camera = self.camera()
		if camera:
			pictureRatio = camera.pictureRatio()
			camera.setPictureRatio(float( resolution.width() ) / resolution.height())
		
		fps = self._scene.animationFPS()
		
		viewportCapture = xsi.Dictionary.GetObject( 'ViewportCapture' ).NestedObjects
		
		viewportCapture( 'File Name' ).Value = fileName
		viewportCapture( 'Padding' ).Value = os.path.basename(genImagePath())
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
		viewportCapture( 'OpenGL Anti-Aliasing' ).Value = 16 if effects else 1
		viewportCapture( 'Remember Last Sequence' ).Value = False

		letterToNumber = { "A":1, "B":2, "C":3, "D":4 }
		xsi.CaptureViewport( letterToNumber[ self.name ], False )
		
		# Restoring states.
		self._scene.restoreViewOptions()
		self.restoreViewOptions()
		
		if camera:
			camera.setPictureRatio(pictureRatio)
		
		# If the famous capture Softimage bug happened we raise a specific error.
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

	def viewOptions(self):
		return self.camera().viewOptions()
		
	def setViewOptions( self, viewOptions ):
		return self.camera().setViewOptions(viewOptions)

	def headlightIsActive( self, state ):
		camera = self._nativeCamera()
		xsi.SetValue( camera.FullName + '.camdisp.headlight', state )
		return True
		
	def setHeadlightIsActive( self ):
		camera = self._nativeCamera()
		return xsi.GetValue( camera.FullName + '.camdisp.headlight' )
		
	def slateIsActive( self ):
		import cross3d
		application = cross3d.application
		version = application.version()
		if version > 9:
			camera = self._nativeCamera()
			return xsi.GetValue( camera.FullName + '.camvis.camerainfo' )
		return False
	
	def setSlateIsActive( self, state ):
		import cross3d
		application = cross3d.application
		version = application.version()
		if version > 9:
			camera = self._nativeCamera()
			xsi.SetValue( camera.FullName + '.camvis.camerainfo', state )
			return True

	def setSlateText( self, text='' ):
		import cross3d
		application = cross3d.application
		version = application.version()
		if version > 9:
			camera = self._nativeCamera()
			xsi.SetValue( camera.FullName + '.camvis.camerainfotext', text )
			return True
		
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneViewport', SoftimageSceneViewport )
