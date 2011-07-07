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
from blur3d.api.abstract.abstractsceneviewport import AbstractSceneViewport

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneViewport( AbstractSceneViewport ):

	def __init__( self, scene, viewportID=0 ):			
		if ( viewportID - 1 ) in range( mxs.viewport.numViews ):
			mxs.viewport.activeViewport = viewportID
		self.name = mxs.viewport.activeViewport

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
		return self._nativeCamera().name
		
	def playblast( self, path, ran=None ):
		
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
		initialGridVisibility = mxs.viewport.getGridVisibility( self.name )
		initialFrame = scene.currentFrame()
		initialSelection = scene.selection()
		initialSafeFrame = mxs.displaySafeFrames
		initialViewNumber = mxs.viewport.numViews

		# getting the camera
		camera = self.camera()
		if camera.hasEffect():
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
		mxs.displaySafeFrames = False
		mxs.viewport.setGridVisibility( self.name, False )
		if initialViewNumber > 1:
			mxs.execute( 'max tool maximize' )
			mxs.completeRedraw()
			
		# getting the viewport size information
		outputSize = [ scene.renderSize().width(), scene.renderSize().height() ]
		viewSize = [ mxs.getViewSize().x, mxs.getViewSize().y ]
		ratios = [ outputSize[0] / viewSize[0] , outputSize[1] / viewSize[1] ]
		if ratios[0] > ratios[1]:
			ratio = ratios[0]
		else:
			ratio = ratios[1]
		playblastSize = [ viewSize[0] * ratio, viewSize[1] * ratio ]
		
		position = [ ( viewSize[0] - playblastSize[0] ) / 2, ( viewSize[1] - playblastSize[1] ) / 2 ]
		mxs.gw.setPos( position[0], position[1], playblastSize[0], playblastSize[1] )
		mxs.completeRedraw()
	
		viewSize = [ mxs.getViewSize().x, mxs.getViewSize().y ]
		crops = [ ( viewSize[0] - outputSize[0] ) / 2, ( viewSize[1] - outputSize[1] ) / 2 ]
		cropsDif = [ viewSize[0] - crops[0], viewSize[1] - crops[1] ]

		for frame in range( ran[0], ran[1] + 1 ):
			scene.setCurrentFrame( frame )
			
			if effects:
				camera.renderEffect()

			imagePath = os.path.join( basePath, '.'.join( [ fileName, str( frame ), fileExtension ] ) )
			image = mxs.gw.getViewportDib()
			animeImage = mxs.bitmap( viewSize[0], viewSize[1] )
			croppedImage = mxs.bitmap( outputSize[0], outputSize[1] )
			croppedImage.filename = imagePath
			mxs.copy( image, animeImage )
			box = mxs.box2( crops[0], crops[1], cropsDif[0], cropsDif[1] )
			mxs.pasteBitmap( animeImage, croppedImage, box, mxs.point2( 0, 0 ) )
			mxs.save( croppedImage ) 
			mxs.close( animeImage )
			mxs.close( croppedImage )

		# restoring viewport settings
		mxs.displaySafeFrames = initialSafeFrame
		mxs.viewport.setGridVisibility( self.name, initialGridVisibility )
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
		if initialViewNumber > 1:
			mxs.execute( 'max tool maximize' )
		else:
			mxs.execute( 'max tool maximize' )
			mxs.completeRedraw()
			mxs.execute( 'max tool maximize' )
		mxs.completeRedraw()
		mxs.gc()

		return True
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneViewport', StudiomaxSceneViewport )
