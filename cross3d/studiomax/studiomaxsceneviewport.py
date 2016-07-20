##
#	\namespace	cross3d.studiomax.studiomaxsceneviewport
#
#	\remarks	The StudiomaxSceneViewport class provides the implementation of the AbstractSceneViewport class as it applies
#				to Softimage scenes
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		04/11/10
#

import os
import time 

from Py3dsMax import mxs
from cross3d import dispatch, application
from cross3d.classes import FrameRange
from cross3d.abstract.abstractsceneviewport import AbstractSceneViewport

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneViewport( AbstractSceneViewport ):

	def __init__( self, scene, viewportID=0 ):		
		super( StudiomaxSceneViewport, self ).__init__( scene, viewportID )
		
		if ( viewportID - 1 ) in range( mxs.viewport.numViews ):
			mxs.viewport.activeViewport = viewportID

		self._scene = scene
		self._nativePointer = mxs.viewport
		self._name = self._nativePointer.activeViewport	
		self._slateIsActive = False
		self._slateText = ''

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _nativeCamera( self ):
		return mxs.viewport.getCamera()
		
	def _setNativeCamera( self, nativeCamera ):
		if type( nativeCamera ) in [ str, unicode ]:
			from cross3d import Scene
			scene = Scene()
			camera = scene._findNativeObject( nativeCamera )
		else:
			camera = nativeCamera
		if nativeCamera:
			mxs.viewport.setCamera( camera )
			self.refresh()
			return True
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def cameraName( self ):
		nativeCamera = self._nativeCamera()
		if nativeCamera:
			return nativeCamera.name
		return None
	
	def size( self ):
		viewSize = mxs.getViewSize()
		return [ viewSize.x, viewSize.y ]
		
	def safeFrameIsActive( self ):
		return mxs.displaySafeFrames
		
	def setSafeFrameIsActive( self, active ):
		mxs.displaySafeFrames = active
		return True

	def createCamera(self, name='Camera', type='Standard'):
		camera = self._scene.createCamera(name, type)
		camera.match(self)
		return camera

	def safeFrameSize( self ):
		scene = self._scene
		outputSize = [ scene.renderSize().width(), scene.renderSize().height() ]
		viewSize = self.size()
		
		ratios = [ float( outputSize[0] ) / viewSize[0] , float( outputSize[1] ) / viewSize[1] ]
		
		if ratios[0] > ratios[1]:
			# cropping height
			outputImageRation = float( outputSize[1] ) / outputSize[0]
			width = viewSize[0]
			height = round( width * outputImageRation )
		else:
			# cropping width
			outputImageRation = float( outputSize[0] ) / outputSize[1]
			height = viewSize[1]
			width = round( height * outputImageRation )
		return [ width, height ]
		
	def safeFrameMargins( self ):
		viewSize = self.size()
		safeFrameSize = self.safeFrameSize()
		horizontal = round( ( viewSize[0] - safeFrameSize[0] ) / 2 )
		vertical = round( ( viewSize[1] - safeFrameSize[1] ) / 2 )
		return [ horizontal, vertical ]

	def generateSnapshot(self, fileName, **options):
		'''TODO: Options are not implemented.'''

		image = mxs.gw.getViewportDib()
		image.filename = fileName
		mxs.save(image)

	def generatePlayblast( self, path, frameRange=None, resolution=None, slate='', effects=None, geometryOnly=True, pathFormat=r'{basePath}\{fileName}.{frame}.{ext}'):
		'''
			/option <bool> effects
		'''
		
		# Treating inputs.
		if isinstance(frameRange, int):
			frameRange = FrameRange([frameRange, frameRange])
			
		# collecting what we need
		scene = self._scene
		basePath, fn = os.path.split(path)
		fileSplit = fn.split( '.' )
		fileName = '.'.join( fileSplit[:-1] )
		initialRange = scene.animationRange()
		fileExtension = fileSplit[-1]
		
		# Creating folder if does not exist.
		dirName = os.path.dirname(path)
		if not os.path.exists(dirName):
			os.makedirs(dirName)

		# Checking inputs.
		if not frameRange:
			frameRange = initialRange
		if not resolution:
			resolution = scene.renderSize()
			
		# Setting slates.
		if slate:
			self.setSlateText(slate)
			self.setSlateIsActive(True)

		# storing infornation
		initialGeometryVisibility = mxs.hideByCategory.geometry
		initialShapesVisibility = mxs.hideByCategory.shapes
		initialLightsVisibility = mxs.hideByCategory.lights
		initialCamerasVisibility = mxs.hideByCategory.cameras
		initialHelpersVisibility = mxs.hideByCategory.helpers
		initialSpaceWarpsVisibility = mxs.hideByCategory.spacewarps
		initialParticleSystemsVisibility = mxs.hideByCategory.particles
		initialBoneObjectsVisibility = mxs.hideByCategory.bones
		initialGridVisibility = mxs.viewport.getGridVisibility( self._name )
		initialFrame = scene.currentFrame()
		initialSelection = scene.selection()
		initialSafeFrame = mxs.displaySafeFrames
		initialViewNumber = mxs.viewport.numViews

		# Getting the camera.
		camera = self.camera()
		
		# setting the scene
		scene.setAnimationRange( frameRange )
		
		# Setting the viewport.
		if geometryOnly:
			mxs.hideByCategory.geometry = False
			mxs.hideByCategory.shapes = True
			mxs.hideByCategory.lights = True
			mxs.hideByCategory.cameras = True
			mxs.hideByCategory.helpers = True
			mxs.hideByCategory.spacewarps = True
			mxs.hideByCategory.particles = False
			mxs.hideByCategory.bones = True
			
		scene.clearSelection()
		mxs.displaySafeFrames = False
		mxs.viewport.setGridVisibility( self._name, False )
		if initialViewNumber > 1:
			mxs.execute( 'max tool maximize' )
			
		# getting the viewport size information
		viewSize = self.size()
		completed = True 
		count = 0
		
		mxs.pyhelper.setViewportQuadSize( resolution.width(), resolution.height() )

		# Should we compute multi-pass effects.
		effects = camera.hasMultiPassEffects() and effects in [None, True]

		# This is my crappy way of figuring out if we are using Nitrous.
		nitrous = not mxs.gw.GetDriverString() and application.version() >= 15

		# We are going to use progressive rendering if the mode is set to Depth of Field (Mental Ray).
		physical = mxs.classof(camera.nativePointer()) in (mxs.VRayPhysicalCamera, mxs.Physical)
		progressive = nitrous and (physical or mxs.classof(camera.nativePointer().mpassEffect) == mxs.Depth_of_Field__mental_ray)

		# If the viewport is using Nitrous.
		if camera and effects and progressive:

			# Storing and setting up Nitrous options.
			nitrousSettings = mxs.NitrousGraphicsManager.GetActiveViewportSetting()
			initialFadingFactor = nitrousSettings.ProgressiveFadingFactor 
			nitrousSettings.ProgressiveFadingFactor = 0
			
		# For each frame.	
		for frame in range( frameRange[0], frameRange[1] + 1 ):
			image = None
			count = count + 1

			# Watching for Esc key.
			if mxs.keyboard.escPressed:
				completed = False
				break
			scene.setCurrentFrame(frame)

			if camera:
				if effects:

					# If we use a Nitrous viewport, we compute the depth of field the new way.
					passes = 0
					if progressive:
						while not mxs.NitrousGraphicsManager.isProgressiveRenderingFinished():
							mxs.NitrousGraphicsManager.progressiveRendering()
							passes += 1
							if passes == 32:
								break

					# Otherwise we compute it the old way by using the API method.
					else:
						camera.renderMultiPassEffects()

					# Text overlays are only supported until Max 2011.
					if slate and application.version() <= 13:
						self.slateDraw()	

				# For Max 2012 and above only the viewport object allows to save the picture with multipass effects.
				if application.version() >= 14 and effects:
					image = mxs.viewport.getViewportDib()

			if not image:
				image = mxs.gw.getViewportDib()

			imagePath = pathFormat.format(basePath=basePath, fileName=fileName, frame=frame, ext=fileExtension)
			image.filename = imagePath
			mxs.save(image)

			# Updating count.
			if count == 100:
				mxs.gc()
				count = 0
		
		# Restoring scene settings.
		scene.setAnimationRange(initialRange)
		
		# Restoring viewport settings.
		self._name = mxs.viewport.activeViewport
		self.slateClear()	
		scene.setSelection( initialSelection )
		scene.setCurrentFrame( initialFrame )
		mxs.displaySafeFrames = initialSafeFrame
		mxs.hideByCategory.geometry = initialGeometryVisibility
		mxs.hideByCategory.shapes =	initialShapesVisibility
		mxs.hideByCategory.lights =	initialLightsVisibility 
		mxs.hideByCategory.cameras = initialCamerasVisibility 
		mxs.hideByCategory.helpers = initialHelpersVisibility
		mxs.hideByCategory.spacewarps =	initialSpaceWarpsVisibility 
		mxs.hideByCategory.particles = initialParticleSystemsVisibility
		mxs.hideByCategory.bones = initialBoneObjectsVisibility
		mxs.viewport.setGridVisibility( self._name, initialGridVisibility )
		mxs.pyhelper.setViewportQuadSize( viewSize[0], viewSize[1] )
		self.setSlateIsActive( False )

		# Restoring Nitrous settings.
		if camera and progressive and camera.hasMultiPassEffects() and effects in [None, True]:

			# Restoring Nitrous settings.
			nitrousSettings.ProgressiveFadingFactor = initialFadingFactor
			
		if initialViewNumber != 1:
			mxs.execute( 'max tool maximize' )

		# After storing all these bitmaps. We make sure to flush Max's memory.
		mxs.gc()
		
		return completed
		
	def slateDraw( self ):
		# processing the text
		import re
		scene = self._scene
		text = self._slateText
		matches = re.findall( r'(\[)([F|f][R|r][A|a][M|m][E|e])( +)?(#[0-9]+)?( +)?(\])', text )
		for match in matches:
			padding = match[3]
			if padding:
				padding = int( padding.strip( '#' ) )
			else:
				padding = 1
			text = text.replace( ''.join( match ), str( scene.currentFrame() ).zfill( padding ) )

		# rendering the slate
		text = text + '  '
		viewSize = self.size()
		textSize = mxs.GetTextExtent( text )
		textWidth = int( textSize.x )
		if self.safeFrameIsActive():
			safeFrameSize = self.safeFrameSize()
			safeFrameMargins = self.safeFrameMargins()
			hMargin = safeFrameMargins[0]
			vMargin = safeFrameMargins[1]
		else:
			hMargin = 0
			vMargin = 0

		textPos = mxs.point3( viewSize[0] - textWidth - hMargin, vMargin, 0 )
		color = mxs.color( 255,255,255 )
		mxs.gw.htext( textPos, text, color=color )
		mxs.gw.enlargeUpdateRect( mxs.pyhelper.namify( 'whole' ) )
		mxs.gw.updatescreen() 

	def slateIsActive( self ):
		return self._slateIsActive
	
	def setSlateIsActive( self, isActive ):
		if isActive:
			if not self._slateIsActive:
				dispatch.connect( 'viewportRedrawn', self.slateDraw )
				mxs.completeRedraw()
			self._slateIsActive = True
			return True
		if self._slateIsActive:
			dispatch.disconnect( 'viewportRedrawn', self.slateDraw )
			self.slateClear()
			self._slateIsActive = False
			return True
		return False

	def refresh( self ):
		mxs.redrawViews()
		return True
		
	def slateText( self ):
		return self._slateText
		
	def slateClear( self ):
		mxs.forceCompleteRedraw()
		
	def setSlateText( self, text ):
		self._slateText = text
		return True
	
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneViewport', StudiomaxSceneViewport )
