##
#	\namespace	blur3d.api.studiomax.studiomaxscenecamera
#
#	\remarks	The StudiomaxSceneCamera class provides the implementation of the AbstractSceneCamera class as it applies
#				to 3d Studio Max scenes
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax import mxs
from blur3d.api.abstract.abstractscenecamera import AbstractSceneCamera

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneCamera( AbstractSceneCamera ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def cameraType( self ):
		"""
			\remarks	implements the AbstractSceneCamera.cameraType method to determine what type of camera this instance is
			\return		<blur3d.api.constants.CameraType>
		"""
		from blur3d.constants import CameraType
		
		cls = mxs.classof(self._nativePointer)
		if ( cls in (mxs.FreeCamera,mxs.TargetCamera) ):
			return CamearType.Standard
		
		elif ( cls == mxs.VRayPhysicalCamera ):
			return CameraType.VRayPhysical
		return 0
		
	def lens( self ):
		return mxs.cameraFOV.FOVtoMM( self.nativePointer().fov )
		
	def hasMultiPassEffects( self ):
		return self.nativePointer().mpassEnabled
		
	def renderMultiPassEffects( self ):
		mxs.maxOps.displayActiveCameraViewWithMultiPassEffect()
		return True
		
	def generateDotXSI( self, path, range=None ):
		import os
		mxs._blurLibrary.load( 'blurXSI' )
		mxs._blurLibrary.load( 'blurCamera' )
		
		outputType = 'Animation'
		sampleType = 'regular'
		sampleRate = 1
		handles = 5
		nativeCamera = self.nativePointer()
		start = str( range[0] )
		end = str( range[1] )	
		initialName = self.displayName()
		model = self.model()
		iteration = model.iteration()
		if not type( iteration ) in [ float, int ]:
			raise Exception( model.name(), 'does not describe a shot number.' )
			return None	
		blurCamIteration = model.iterationString( 4, 2, '-', True )
		blurName = '_'.join( [ 'S', blurCamIteration, '', start + '-' + end, '' ] )
		shotNumber = float( iteration )

		# adding the blur properties and setting the name of the camera
		mxs._blurCamera.SetCameraInfo( [ shotNumber, 'A', start, end ] );

		# write the file
		mxs._blurXSI.fileWrite(	path, outputType , shotNumber , range[0], range[1], sampleType, sampleRate, (range[0] - handles), (range[1] + handles), [nativeCamera] )
		
		# restore camera
		self.setDisplayName( initialName )

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', StudiomaxSceneCamera )