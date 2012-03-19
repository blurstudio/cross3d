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

		self._scene = scene
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

	def generatePlayblast( self, path, ran=None, **options ):
		'''
			/option <bool> effects
		'''

		# collecting what we need
		import os
		scene = self._scene
		pathSplit = os.path.split( path )
		basePath = pathSplit[0]
		file = pathSplit[1]
		fileSplit = file.split( '.' )
		fileName = '.'.join( fileSplit[:-1] )
		fileExtension = 'jpg'
		effects = options.get( 'effects', True )
		initialRange = scene.animationRange()
		application = self._scene.application()
		
		# checking inputs
		if not ran:
			ran = initialRange

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
		
		# setting the scene
		scene.setAnimationRange( ran )
		
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
		mxs.displaySafeFrames = False
		mxs.viewport.setGridVisibility( self._name, False )
		if initialViewNumber > 1:
			mxs.execute( 'max tool maximize' )
			
		# getting the viewport size information
		viewSize = self.size()
		completed = True 
		count = 0
		
		mxs.pyhelper.setViewportQuadSize( scene.renderSize().width(), scene.renderSize().height() )

		for frame in range( ran[0], ran[1] + 1 ):
			count = count + 1
			if mxs.keyboard.escPressed:
				completed = False
				break
			scene.setCurrentFrame( frame )
			
			if camera:
				if camera.hasMultiPassEffects() and effects:
					camera.renderMultiPassEffects()
					if application.version() != 14:
						self.slateDraw()	

			imagePath = os.path.join( basePath, '.'.join( [ fileName, str( frame ), fileExtension ] ) )
			image = mxs.viewport.getViewportDib()
			image.filename = imagePath
			mxs.save( image )
			if count == 100:
				mxs.gc()
				count = 0
		
		# restoring the scene
		scene.setAnimationRange( initialRange )
		
		# restoring viewport settings
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
		
		if initialViewNumber != 1:
			mxs.execute( 'max tool maximize' )

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
from blur3d import api
api.registerSymbol( 'SceneViewport', StudiomaxSceneViewport )
