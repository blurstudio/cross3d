##
#	\namespace	blur3d.api.studiomax.studiomaxsceneviewport
#
#	\remarks	The StudiomaxSceneViewport class provides the implementation of the AbstractSceneViewport class as it applies
#				to Softimage scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/11/10
#

from Py3dsMax import mxs
from blur3d.api import dispatch
from blur3d.api.abstract.abstractsceneviewport import AbstractSceneViewport

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneViewport( AbstractSceneViewport ):

	def __init__( self, scene, viewportID=0 ):		
		super( StudiomaxSceneViewport, self ).__init__( scene, viewportID )
		
		if ( viewportID - 1 ) in range( mxs.viewport.numViews ):
			mxs.viewport.activeViewport = viewportID

		self._name = mxs.viewport.activeViewport	
		self._slateIsActive = False
		self._slateText = ''

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _nativeCamera( self ):
		return mxs.viewport.getCamera()
		
	def _setNativeCamera( self, nativeCamera ):
		if type( nativeCamera ) in [ str, unicode ]:
			from blur3d.api import Scene
			scene = Scene()
			camera = scene._findNativeObject( nativeCamera )
		else:
			camera = nativeCamera
		if nativeCamera:
			mxs.viewport.setCamera( camera )
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
		return [ mxs.getViewSize().x, mxs.getViewSize().y ]
		
	def safeFrameIsActive( self ):
		return mxs.displaySafeFrames
		
	def setSafeFrameIsActive( self, active ):
		mxs.displaySafeFrames = active
		return True

	def safeFrameSize( self ):
		from blur3d.api import Scene
		scene = Scene()
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

	def generatePlayblast( self, path, ran=None ):
		# collecting what we need
		import os
		from blur3d.api import Scene
		scene = Scene()
		pathSplit = os.path.split( path )
		basePath = pathSplit[0]
		file = pathSplit[1]
		fileSplit = file.split( '.' )
		fileName = '.'.join( fileSplit[:-1] )
		fileExtension = 'jpg'
		effects = False
		
		# checking inputs
		if not ran:
			ran = scene.animationRange()

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

		# getting the camera
		camera = self.camera()
		if camera.hasMultiPassEffects():
			effects = True
			
		# setting the viewport
		mxs.hideByCategory.geometry = False
		mxs.hideByCategory.shapes = True
		mxs.hideByCategory.lights = True
		mxs.hideByCategory.cameras = True
		mxs.hideByCategory.helpers = True
		mxs.hideByCategory.spacewarps = True
		mxs.hideByCategory.particles = False
		mxs.hideByCategory.bones = True
		scene.clearSelection()
		mxs.displaySafeFrames = True
		mxs.viewport.setGridVisibility( self._name, False )
		if initialViewNumber > 1:
			mxs.execute( 'max tool maximize' )
			mxs.completeRedraw()
			
		# getting the viewport size information
		outputSize = [ scene.renderSize().width(), scene.renderSize().height() ]
		viewSize = self.size()
		ratios = [ outputSize[0] / viewSize[0] , outputSize[1] / viewSize[1] ]
		if ratios[0] > ratios[1]:
			ratio = ratios[0]
		else:
			ratio = ratios[1]
		playblastSize = [ viewSize[0] * ratio, viewSize[1] * ratio ]
		
		position = [ ( viewSize[0] - playblastSize[0] ) / 2, ( viewSize[1] - playblastSize[1] ) / 2 ]
		mxs.gw.setPos( position[0], position[1], playblastSize[0], playblastSize[1] )
	
		viewSize = [ mxs.getViewSize().x, mxs.getViewSize().y ]
		crops = [ ( viewSize[0] - outputSize[0] ) / 2, ( viewSize[1] - outputSize[1] ) / 2 ]
		cropsDif = [ viewSize[0] - crops[0], viewSize[1] - crops[1] ]
		box = mxs.box2( crops[0], crops[1], cropsDif[0], cropsDif[1] )
		croppedImage = mxs.bitmap( outputSize[0], outputSize[1] )
		completed = True 
		count = 0
		
		for frame in range( ran[0], ran[1] + 1 ):
			count = count + 1
			if mxs.keyboard.escPressed:
				completed = False
				break
			scene.setCurrentFrame( frame )
			
			if effects:
				camera.renderMultiPassEffects()
				self.slateDraw()	

			imagePath = os.path.join( basePath, '.'.join( [ fileName, str( frame ), fileExtension ] ) )
			image = mxs.gw.getViewportDib()
			croppedImage.filename = imagePath
			mxs.pasteBitmap( image, croppedImage, box, mxs.point2( 0, 0 ) )
			mxs.save( croppedImage )
			if count == 100:
				mxs.gc()
				count = 0
			
		# restoring viewport settings
		self.slateClear()	
		mxs.displaySafeFrames = initialSafeFrame
		scene.setSelection( initialSelection )
		scene.setCurrentFrame( initialFrame )
		mxs.hideByCategory.geometry = initialGeometryVisibility
		mxs.hideByCategory.shapes =	initialShapesVisibility
		mxs.hideByCategory.lights =	initialLightsVisibility 
		mxs.hideByCategory.cameras = initialCamerasVisibility 
		mxs.hideByCategory.helpers = initialHelpersVisibility
		mxs.hideByCategory.spacewarps =	initialSpaceWarpsVisibility 
		mxs.hideByCategory.particles = initialParticleSystemsVisibility
		mxs.hideByCategory.bones = initialBoneObjectsVisibility
		if initialViewNumber == 1:
			mxs.execute( 'max tool maximize' )
		mxs.execute( 'max tool maximize' )
		self._name = mxs.viewport.activeViewport
		mxs.viewport.setGridVisibility( self._name, initialGridVisibility )
		mxs.gc()
		return completed
		
	def slateDraw( self ):
		# importing stuff
		import re
		from blur3d.api import Scene
		scene = Scene()
		
		# processing the text
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
		
		# I am not very happy with the posX calculation as the textWidth does not seem to be very reliable.
		textPos = mxs.point3( viewSize[0] - textWidth - hMargin, vMargin, 0 )
		colorWhite = mxs.color( 255,255,255 )
		mxs.gw.htext( textPos, text, color=colorWhite )
		box = mxs.box2( 0,0,viewSize[0],viewSize[1] )
		mxs.gw.enlargeUpdateRect( box )
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

	def slateText( self ):
		return self._slateText
		
	def slateClear( self ):
		mxs.forceCompleteRedraw()
		
	def setSlateText( self, text ):
		self._slateText = text
		return True
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', StudiomaxSceneViewport )
