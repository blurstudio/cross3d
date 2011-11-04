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

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', StudiomaxSceneCamera )